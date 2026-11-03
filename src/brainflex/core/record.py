"""Record the start and end of experiment steps."""

import warnings
from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    COL_ANSWER,
    COL_QUESTION,
    COL_STATUS,
    COL_STEP,
    COL_TIMESTAMP,
    LIKERT_CHOICES,
    QUESTION_NOTES,
    QUESTION_TIME_WITHOUT_TOOLS,
    QUESTION_TOOLS_EASIER,
    STEP_SURVEY_COLUMNS,
    STEP_SURVEY_FILENAME,
    TIME_WITHOUT_TOOLS_CHOICES,
    TIMESTAMPS_COLUMNS,
    TIMESTAMPS_FILENAME,
)
from brainflex.utils.tsv import append_tsv, load_tsv


class Step(StrEnum):
    """Experiment steps."""

    IDP_EXTRACTION = "idp_extraction"
    SEMANTIC_HARMONIZATION = "semantic_harmonization"
    FL_READY_DATA = "fl_ready_data"
    FEDBIOMED_NODE_PART_1 = "fedbiomed_node_part_1"
    FEDBIOMED_NODE_PART_2 = "fedbiomed_node_part_2"


class Status(StrEnum):
    """Step statuses."""

    START = "start"
    END = "end"


DATA_PREP_STEPS = frozenset(
    {Step.IDP_EXTRACTION, Step.SEMANTIC_HARMONIZATION, Step.FL_READY_DATA}
)

# questions asked at the end of a step, mapped to their allowed answers
# (None for free text), in the order they are asked
DATA_PREP_QUESTIONS: dict[str, tuple[str, ...] | None] = {
    QUESTION_TOOLS_EASIER: LIKERT_CHOICES,
    QUESTION_TIME_WITHOUT_TOOLS: TIME_WITHOUT_TOOLS_CHOICES,
}
COMMON_QUESTIONS: dict[str, tuple[str, ...] | None] = {QUESTION_NOTES: None}


def get_step_questions(step: Step) -> dict[str, tuple[str, ...] | None]:
    """Return the questions asked at the end of a step, mapped to allowed answers."""
    if step in DATA_PREP_STEPS:
        return DATA_PREP_QUESTIONS | COMMON_QUESTIONS
    return dict(COMMON_QUESTIONS)


def _check_answers(
    step: Step, status: Status, answers: Mapping[str, str]
) -> dict[str, tuple[str, ...] | None]:
    """Raise ValueError if the answers don't match the questions for the step."""
    questions = get_step_questions(step) if status == Status.END else {}
    if set(answers) != set(questions):
        raise ValueError(
            f"Answers for {step} {status} must be given for exactly these"
            f" questions: {list(questions)}"
        )
    for question, answer in answers.items():
        choices = questions[question]
        if choices is not None and answer not in choices:
            raise ValueError(
                f"Invalid answer {answer!r} to {question!r}:"
                f" must be one of {', '.join(choices)}"
            )
    return questions


def record(
    root: Path,
    step: Step,
    status: Status,
    answers: Mapping[str, str] | None = None,
) -> tuple[Path, Path | None]:
    """Record the start or end of a step + some survey answers.

    Returns the paths to the timestamps file and to the survey file (if applicable).
    """
    answers = answers or {}
    questions = _check_answers(step, status, answers)

    dpath = root / BRAINFLEX_DIRNAME
    fpath_timestamps = dpath / TIMESTAMPS_FILENAME
    df_timestamps = load_tsv(fpath_timestamps, TIMESTAMPS_COLUMNS)

    statuses = df_timestamps.query(f"{COL_STEP} == @step")[COL_STATUS]
    last_status = statuses.iloc[-1] if not statuses.empty else None
    if status == Status.START and last_status == Status.START:
        warnings.warn(f"step {step} was already started", stacklevel=2)
    elif status == Status.END and last_status != Status.START:
        warnings.warn(f"step {step} was not started", stacklevel=2)

    row = {
        COL_TIMESTAMP: datetime.now().astimezone().isoformat(timespec="seconds"),
        COL_STEP: str(step),
        COL_STATUS: str(status),
    }
    append_tsv(fpath_timestamps, TIMESTAMPS_COLUMNS, [row], df=df_timestamps)

    if not questions:
        return fpath_timestamps, None

    fpath_survey = dpath / STEP_SURVEY_FILENAME
    append_tsv(
        fpath_survey,
        STEP_SURVEY_COLUMNS,
        (
            {COL_STEP: str(step), COL_QUESTION: q, COL_ANSWER: answers[q]}
            for q in questions
        ),
    )
    return fpath_timestamps, fpath_survey
