"""Download an OpenNeuro dataset into a Nipoppy study."""

import csv
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from nipoppy.env import FAKE_SESSION_ID
from nipoppy.layout import DatasetLayout

from brainflex.utils.constants import (
    BIDS_SESSION_PREFIX,
    BIDS_SUBJECT_PREFIX,
    BRAINFLEX_DIRNAME,
    COL_PARTICIPANT_ID,
    DATA_DIRNAME,
    DERIVATIVES_BUCKET,
    DERIVATIVES_REGION,
    FREESURFER_BUILD_STAMP,
    FREESURFER_PIPELINE_NAME,
    FREESURFER_PREFIX,
    FREESURFER_SUBDIRS,
    OPENNEURO_BUCKET,
    OPENNEURO_REGION,
    PARTICIPANTS_FILENAME,
    PHENO_FILENAME,
)
from brainflex.utils.s3 import download, list_keys, make_store, read


def _stage_bids(dataset_id: str, dpath: Path) -> None:
    """Download top-level BIDS files and create empty placeholders for the rest."""
    store = make_store(OPENNEURO_BUCKET, OPENNEURO_REGION)
    prefix = f"{dataset_id}/"
    keys = list_keys(store, prefix)
    if not keys:
        raise ValueError(f"Dataset not found on OpenNeuro: {dataset_id}")

    keys_to_paths = {}
    for key in keys:
        relpath = key.removeprefix(prefix)
        if relpath.endswith("/"):
            continue
        if "/" not in relpath:
            keys_to_paths[key] = dpath / relpath
        elif relpath.startswith(BIDS_SUBJECT_PREFIX):
            fpath = dpath / relpath
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.touch()
    dpath.mkdir(parents=True, exist_ok=True)
    download(store, keys_to_paths)


def _get_session_ids(dpath_bids: Path) -> dict[str, str]:
    """Map each BIDS subject to its (single) BIDS session ID."""
    session_ids = {}
    for dpath_subject in sorted(dpath_bids.glob(f"{BIDS_SUBJECT_PREFIX}*")):
        if not dpath_subject.is_dir():
            continue
        sessions = sorted(
            p.name for p in dpath_subject.glob(f"{BIDS_SESSION_PREFIX}*") if p.is_dir()
        )
        if len(sessions) > 1:
            raise ValueError(
                f"Multi-session datasets are not supported: {dpath_subject.name}"
                f" has sessions {sessions}"
            )
        session_ids[dpath_subject.name] = (
            sessions[0] if sessions else f"{BIDS_SESSION_PREFIX}{FAKE_SESSION_ID}"
        )
    return session_ids


def _get_freesurfer(
    dataset_id: str, layout: DatasetLayout, session_ids: dict[str, str]
) -> None:
    """Download FreeSurfer outputs into the Nipoppy derivatives directory."""
    store = make_store(DERIVATIVES_BUCKET, DERIVATIVES_REGION)
    prefix = FREESURFER_PREFIX.format(dataset_id=dataset_id) + "/"

    # key format: <prefix><subject>/<subdir>/<path>
    keys = []
    for key in list_keys(store, prefix):
        parts = key.removeprefix(prefix).split("/")
        if (
            len(parts) > 2
            and parts[0] in session_ids
            and parts[1] in FREESURFER_SUBDIRS
        ):
            keys.append(key)
    if not keys:
        raise ValueError(f"No FreeSurfer derivatives found for {dataset_id}")

    build_stamp_key = next(
        (k for k in keys if k.endswith(f"/{FREESURFER_BUILD_STAMP}")), None
    )
    if build_stamp_key is None:
        raise ValueError(f"No FreeSurfer build stamp found for {dataset_id}")
    build_stamp = read(store, build_stamp_key).decode()
    match = re.search(r"v(\d+\.\d+\.\d+)", build_stamp)
    if match is None:
        raise ValueError(f"Could not parse FreeSurfer version from: {build_stamp}")
    version = match.group(1)

    dpath_output = layout.get_dpath_pipeline_output(FREESURFER_PIPELINE_NAME, version)
    keys_to_paths = {}
    for key in keys:
        relpath = key.removeprefix(prefix)
        subject = relpath.split("/", 1)[0]
        keys_to_paths[key] = dpath_output / session_ids[subject] / relpath
    download(store, keys_to_paths)


def _write_pheno(layout: DatasetLayout) -> None:
    """Copy participants.tsv to the tabular directory, with sub- prefixed IDs."""
    fpath_participants = layout.dpath_bids / PARTICIPANTS_FILENAME
    if not fpath_participants.is_file():
        raise ValueError(f"No {PARTICIPANTS_FILENAME} found in {layout.dpath_bids}")

    with fpath_participants.open(newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Neurobagel requires the sub- prefix
    for row in rows:
        participant_id = row[COL_PARTICIPANT_ID]
        if not participant_id.startswith(BIDS_SUBJECT_PREFIX):
            row[COL_PARTICIPANT_ID] = f"{BIDS_SUBJECT_PREFIX}{participant_id}"

    layout.dpath_tabular.mkdir(parents=True, exist_ok=True)
    with (layout.dpath_tabular / PHENO_FILENAME).open("w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=fieldnames, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def get_data(root: Path, dataset_id: str, overwrite: bool = False) -> Path:
    """Download an OpenNeuro dataset and format it as a Nipoppy study.

    Dataset must be cross-sectional (with or without session-level subdirectories)
    and have FreeSurfer derivative data.

    To optimize disk space, raw BIDS imaging files are empty placeholders, and
    FreeSurfer outputs contain stats/ and scripts/ only.

    Raises FileExistsError if the study already exists and ``overwrite`` is False.
    Returns the path to the Nipoppy study.
    """
    dpath_study = root / DATA_DIRNAME / dataset_id
    if dpath_study.exists():
        if not overwrite:
            raise FileExistsError(f"Dataset already exists: {dpath_study}")
        shutil.rmtree(dpath_study)

    dpath_brainflex = root / BRAINFLEX_DIRNAME
    dpath_brainflex.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dpath_brainflex) as dpath_tmp:
        dpath_staging = Path(dpath_tmp) / dataset_id
        _stage_bids(dataset_id, dpath_staging)
        subprocess.run(
            [
                "nipoppy",
                "init",
                "--dataset",
                str(dpath_study),
                "--bids-source",
                str(dpath_staging),
                "--mode",
                "move",
            ],
            check=True,
            capture_output=True,
        )

    layout = DatasetLayout(dpath_root=dpath_study)
    session_ids = _get_session_ids(layout.dpath_bids)
    _get_freesurfer(dataset_id, layout, session_ids)
    _write_pheno(layout)
    return dpath_study
