import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from brainflex.core.get_data import get_data
from brainflex.core.init import init
from brainflex.utils.constants import (
    DATA_DIRNAME,
    DERIVATIVES_BUCKET,
    OPENNEURO_BUCKET,
)

DATASET_ID = "ds000001"
FS_PREFIX = f"fmriprep/{DATASET_ID}-fmriprep/sourcedata/freesurfer"
BUILD_STAMP = b"freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.1-f53a55a\n"


def _raw_objects(subject_dirs: list[str]) -> dict[tuple[str, str], bytes]:
    objects = {
        (OPENNEURO_BUCKET, f"{DATASET_ID}/dataset_description.json"): b"{}",
        (OPENNEURO_BUCKET, f"{DATASET_ID}/participants.json"): b'{"age": {}}',
        (OPENNEURO_BUCKET, f"{DATASET_ID}/participants.tsv"): (
            b"participant_id\tage\nsub-01\t20\nsub-02\t30\nsub-03\t40\n"
        ),
        (OPENNEURO_BUCKET, f"{DATASET_ID}/derivatives/file.txt"): b"skipped",
        (OPENNEURO_BUCKET, f"{DATASET_ID}/sub-01/"): b"",
    }
    for subject_dir in subject_dirs:
        subject = subject_dir.split("/")[0]
        key = f"{DATASET_ID}/{subject_dir}/anat/{subject}_T1w.nii.gz"
        objects[(OPENNEURO_BUCKET, key)] = b"image"
    return objects


def _fs_objects(subjects: list[str]) -> dict[tuple[str, str], bytes]:
    objects = {(DERIVATIVES_BUCKET, f"{FS_PREFIX}/fsaverage/surf/lh.white"): b"fs"}
    for subject in subjects:
        objects |= {
            (DERIVATIVES_BUCKET, f"{FS_PREFIX}/{subject}/stats/aseg.stats"): b"aseg",
            (
                DERIVATIVES_BUCKET,
                f"{FS_PREFIX}/{subject}/scripts/build-stamp.txt",
            ): BUILD_STAMP,
            (DERIVATIVES_BUCKET, f"{FS_PREFIX}/{subject}/mri/T1.mgz"): b"skipped",
        }
    return objects


@pytest.fixture
def objects() -> dict[tuple[str, str], bytes]:
    return _raw_objects(["sub-01", "sub-02"]) | _fs_objects(
        ["sub-01", "sub-02", "sub-99"]
    )


@pytest.fixture
def mock_s3(
    mocker: MockerFixture, objects: dict[tuple[str, str], bytes]
) -> dict[tuple[str, str], bytes]:
    # stores are represented by their bucket name
    def fake_list_keys(store: str, prefix: str) -> list[str]:
        return [k for b, k in objects if b == store and k.startswith(prefix)]

    def fake_read(store: str, key: str) -> bytes:
        return objects[(store, key)]

    def fake_download(
        store: str,
        keys_to_paths: dict[str, Path],
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        for key, path in keys_to_paths.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(objects[(store, key)])
            if on_complete is not None:
                on_complete()

    module = "brainflex.core.get_data"
    mocker.patch(f"{module}.make_store", side_effect=lambda bucket, region: bucket)
    mocker.patch(f"{module}.list_keys", side_effect=fake_list_keys)
    mocker.patch(f"{module}.read", side_effect=fake_read)
    mocker.patch(f"{module}.download", side_effect=fake_download)
    return objects


@pytest.fixture
def root(tmp_path: Path) -> Path:
    init(tmp_path)
    return tmp_path


class TestGetData:
    def test_get_data(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        dpath_study = get_data(root, DATASET_ID)
        assert dpath_study == root / DATA_DIRNAME / DATASET_ID

        # BIDS: top-level files downloaded, subject files are empty placeholders
        dpath_bids = dpath_study / "bids"
        assert (dpath_bids / "dataset_description.json").read_bytes() == b"{}"
        assert (
            dpath_bids / "sub-01" / "anat" / "sub-01_T1w.nii.gz"
        ).stat().st_size == 0
        assert not (dpath_bids / "derivatives").exists()

        manifest = (dpath_study / "manifest.tsv").read_text()
        assert "\n01\t" in manifest
        assert "\n02\t" in manifest

        # FreeSurfer: only stats/scripts, only BIDS subjects
        dpath_output = dpath_study / "derivatives/freesurfer/6.0.1/output/ses-unnamed"
        assert sorted(p.name for p in dpath_output.iterdir()) == ["sub-01", "sub-02"]
        assert (dpath_output / "sub-01/stats/aseg.stats").read_bytes() == b"aseg"
        assert (dpath_output / "sub-01/scripts/build-stamp.txt").is_file()
        assert not (dpath_output / "sub-01/mri").exists()

        pheno = (dpath_study / "tabular" / "pheno.tsv").read_text()
        # sub-03 has no imaging data
        assert pheno == (
            "participant_id\tsession_id\tage\n"
            "sub-01\tses-unnamed\t20\n"
            "sub-02\tses-unnamed\t30\n"
            "sub-03\t\t40\n"
        )
        pheno_json = (dpath_study / "tabular" / "pheno.json").read_text()
        assert pheno_json == '{"age": {}}'

        # staging directory is cleaned up
        assert sorted(p.name for p in (root / ".brainflex").iterdir()) == [
            "status_log.tsv"
        ]

    def test_no_participants_json(
        self, mock_s3: dict[tuple[str, str], bytes], root: Path
    ):
        del mock_s3[(OPENNEURO_BUCKET, f"{DATASET_ID}/participants.json")]
        dpath_study = get_data(root, DATASET_ID)
        assert (dpath_study / "tabular" / "pheno.tsv").is_file()
        assert not (dpath_study / "tabular" / "pheno.json").exists()

    def test_full_rawbids(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        dpath_study = get_data(root, DATASET_ID, full_rawbids=True)
        fpath = dpath_study / "bids/sub-01/anat/sub-01_T1w.nii.gz"
        assert fpath.read_bytes() == b"image"
        assert not (dpath_study / "bids/derivatives").exists()

    def test_full_freesurfer(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        dpath_study = get_data(root, DATASET_ID, full_freesurfer=True)
        dpath_output = dpath_study / "derivatives/freesurfer/6.0.1/output/ses-unnamed"
        assert sorted(p.name for p in dpath_output.iterdir()) == ["sub-01", "sub-02"]
        assert (dpath_output / "sub-01/mri/T1.mgz").read_bytes() == b"skipped"
        assert (dpath_output / "sub-01/stats/aseg.stats").is_file()

    @pytest.mark.parametrize(
        ("build_stamp", "version"),
        [
            (b"freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.1-f53a55a\n", "6.0.1"),
            (b"freesurfer-linux-ubuntu22_x86_64-7.3.2-20220804-6354275\n", "7.3.2"),
        ],
    )
    def test_freesurfer_version(
        self,
        mock_s3: dict[tuple[str, str], bytes],
        root: Path,
        build_stamp: bytes,
        version: str,
    ):
        for bucket, key in mock_s3:
            if key.endswith("/scripts/build-stamp.txt"):
                mock_s3[(bucket, key)] = build_stamp
        dpath_study = get_data(root, DATASET_ID)
        dpath_pipeline = dpath_study / "derivatives/freesurfer"
        assert [p.name for p in dpath_pipeline.iterdir()] == [version]

    def test_bad_build_stamp(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        for bucket, key in mock_s3:
            if key.endswith("/scripts/build-stamp.txt"):
                mock_s3[(bucket, key)] = b"freesurfer-dev\n"
        with pytest.raises(ValueError, match="Could not parse FreeSurfer version"):
            get_data(root, DATASET_ID)

    def test_single_session(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        mock_s3.clear()
        mock_s3 |= _raw_objects(["sub-01/ses-01", "sub-02/ses-02"]) | _fs_objects(
            ["sub-01", "sub-02"]
        )
        dpath_study = get_data(root, DATASET_ID)
        dpath_output = dpath_study / "derivatives/freesurfer/6.0.1/output"
        assert (dpath_output / "ses-01/sub-01/stats/aseg.stats").is_file()
        assert (dpath_output / "ses-02/sub-02/stats/aseg.stats").is_file()
        pheno = (dpath_study / "tabular" / "pheno.tsv").read_text()
        assert "sub-01\tses-01\t" in pheno
        assert "sub-02\tses-02\t" in pheno

    def test_multiple_sessions(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        mock_s3.clear()
        mock_s3 |= _raw_objects(["sub-01/ses-01", "sub-01/ses-02"]) | _fs_objects(
            ["sub-01"]
        )
        with pytest.raises(ValueError, match="Multi-session"):
            get_data(root, DATASET_ID)

    def test_already_exists(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        dpath_study = root / DATA_DIRNAME / DATASET_ID
        dpath_study.mkdir(parents=True)
        (dpath_study / "file.txt").write_text("keep me")
        with pytest.raises(FileExistsError, match="already exists"):
            get_data(root, DATASET_ID)
        assert (dpath_study / "file.txt").read_text() == "keep me"

    def test_overwrite(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        dpath_study = root / DATA_DIRNAME / DATASET_ID
        dpath_study.mkdir(parents=True)
        (dpath_study / "file.txt").write_text("old")
        get_data(root, DATASET_ID, overwrite=True)
        assert not (dpath_study / "file.txt").exists()
        assert (dpath_study / "manifest.tsv").is_file()

    def test_dataset_not_found(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        mock_s3.clear()
        with pytest.raises(ValueError, match="not found on OpenNeuro"):
            get_data(root, DATASET_ID)

    def test_no_freesurfer(self, mock_s3: dict[tuple[str, str], bytes], root: Path):
        mock_s3.clear()
        mock_s3 |= _raw_objects(["sub-01"])
        with pytest.raises(ValueError, match="No FreeSurfer derivatives"):
            get_data(root, DATASET_ID)

    def test_nipoppy_init_fails(
        self,
        mock_s3: dict[tuple[str, str], bytes],
        root: Path,
        mocker: MockerFixture,
    ):
        mocker.patch(
            "brainflex.core.get_data.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "nipoppy"),
        )
        with pytest.raises(subprocess.CalledProcessError):
            get_data(root, DATASET_ID)
