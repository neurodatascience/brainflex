"""Survey on prior experience, answered before the experiment."""

from pathlib import Path

import pandas as pd

from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    COL_FEDBIOMED_FAMILIARITY,
    COL_NEUROBAGEL_FAMILIARITY,
    COL_NIPOPPY_FAMILIARITY,
    INITIAL_SURVEY_COLUMNS,
    INITIAL_SURVEY_FILENAME,
    LIKERT_CHOICES,
)


def check_initial_survey_path(root: Path, overwrite: bool = False) -> Path:
    """Return the path to the initial survey file of the project.

    Raises FileExistsError if the file already exists and ``overwrite`` is False.
    """
    fpath = root / BRAINFLEX_DIRNAME / INITIAL_SURVEY_FILENAME
    if fpath.exists() and not overwrite:
        raise FileExistsError(
            f"Initial survey already completed: {fpath} exists."
            " Use --overwrite to replace it."
        )
    return fpath


def initial_survey(
    root: Path,
    nipoppy: int,
    neurobagel: int,
    fedbiomed: int,
    overwrite: bool = False,
) -> None:
    """Save the answers to the initial survey.

    Raises ValueError if a rating is out of range, and FileExistsError if the survey
    file already exists and ``overwrite`` is False.
    """
    answers = {
        COL_NIPOPPY_FAMILIARITY: nipoppy,
        COL_NEUROBAGEL_FAMILIARITY: neurobagel,
        COL_FEDBIOMED_FAMILIARITY: fedbiomed,
    }
    for col, value in answers.items():
        if str(value) not in LIKERT_CHOICES:
            raise ValueError(
                f"Invalid {col} {value!r}: must be one of {', '.join(LIKERT_CHOICES)}"
            )

    fpath = check_initial_survey_path(root, overwrite=overwrite)

    pd.DataFrame([answers], columns=INITIAL_SURVEY_COLUMNS).to_csv(
        fpath, sep="\t", index=False
    )
