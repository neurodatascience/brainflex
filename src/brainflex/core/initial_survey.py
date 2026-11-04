"""Survey on prior experience, answered before the experiment."""

from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    COL_ANSWER,
    COL_QUESTION,
    FAMILIARITY_LABELS,
    INITIAL_SURVEY_FILENAME,
    INITIAL_SURVEY_QUESTIONS,
    LIKERT_CHOICES,
    SURVEY_COLUMNS,
)
from brainflex.utils.likert import label_likert_answer


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
    root: Path, answers: Mapping[str, int], overwrite: bool = False
) -> None:
    """Save the answers to the initial survey.

    ``answers`` maps each question in ``INITIAL_SURVEY_QUESTIONS`` to a rating on a
    Likert scale from 1 to 5. Raises ValueError if questions are missing or unknown,
    or if a rating is out of range, and FileExistsError if the survey file already
    exists and ``overwrite`` is False.
    """
    if set(answers) != set(INITIAL_SURVEY_QUESTIONS):
        raise ValueError(
            "Answers must be given for exactly these questions:"
            f" {INITIAL_SURVEY_QUESTIONS}"
        )
    for question, answer in answers.items():
        if str(answer) not in LIKERT_CHOICES:
            raise ValueError(
                f"Invalid answer {answer!r} to {question!r}:"
                f" must be one of {', '.join(LIKERT_CHOICES)}"
            )

    fpath = check_initial_survey_path(root, overwrite=overwrite)

    rows = [
        {
            COL_QUESTION: question,
            COL_ANSWER: label_likert_answer(answers[question], FAMILIARITY_LABELS),
        }
        for question in INITIAL_SURVEY_QUESTIONS
    ]
    pd.DataFrame(rows, columns=SURVEY_COLUMNS).to_csv(fpath, sep="\t", index=False)
