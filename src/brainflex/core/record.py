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
    QUESTION_NOTES,
    QUESTION_TIME_WITHOUT_TOOLS,
    QUESTION_TOOLS_EASIER,
    STEP_SURVEY_COLUMNS,
    STEP_SURVEY_FILENAME,
    TIME_WITHOUT_TOOLS_CHOICES,
    TIMESTAMPS_COLUMNS,
    TIMESTAMPS_FILENAME,
    TOOLS_EASIER_CHOICES,
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
    QUESTION_TOOLS_EASIER: TOOLS_EASIER_CHOICES,
    QUESTION_TIME_WITHOUT_TOOLS: TIME_WITHOUT_TOOLS_CHOICES,
}
COMMON_QUESTIONS: dict[str, tuple[str, ...] | None] = {QUESTION_NOTES: None}

# high-level summaries of data preparation steps
STEP_SUMMARIES: dict[Step, str] = {
    Step.IDP_EXTRACTION: (
        "In this step, you used a script that wraps FreeSurfer tools to:\n- extract "
        "imaging-derived phenotypes (IDPs) (cortical thickness, subcortical volumes, "
        "etc.) from existing FreeSurfer subject directories\n- combine them into "
        "tabular files with standardized structure and column names (shared with every "
        "other site participating in the FL experiment)"
    ),
    Step.SEMANTIC_HARMONIZATION: (
        "In this step, you created a file containing participant IDs, session IDs, and "
        "demographic information (age, sex) that use standardized column names and "
        "values (shared with every other site participating in the FL experiment), "
        "despite the fact that the original demographic data may have used "
        "different names or values."
    ),
    Step.FL_READY_DATA: (
        "In this step, you merged the previously extracted FreeSurfer IDPs and "
        "harmonized phenotypic data into datasets formatted in a way that can be used "
        "directly by the Fed-BioMed federated learning framework. All sites "
        "participating in the FL experiment will have datasets with the same structure "
        "and column names, so that they can be used together to train models."
    ),
}


def get_step_questions(step: Step) -> dict[str, tuple[str, ...] | None]:
    """Return the questions asked at the end of a step, mapped to allowed answers."""
    if step in DATA_PREP_STEPS:
        return DATA_PREP_QUESTIONS | COMMON_QUESTIONS
    return dict(COMMON_QUESTIONS)


def get_step_summary(step: Step) -> str | None:
    """Return a high-level summary of a data preparation step (None otherwise)."""
    return STEP_SUMMARIES.get(step)


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


def check_status(root: Path, step: Step, status: Status) -> None:
    """Warn if a step is started twice or ended without being started."""
    df_timestamps = load_tsv(
        root / BRAINFLEX_DIRNAME / TIMESTAMPS_FILENAME, TIMESTAMPS_COLUMNS
    )
    statuses = df_timestamps.query(f"{COL_STEP} == @step")[COL_STATUS]
    last_status = statuses.iloc[-1] if not statuses.empty else None
    if status == Status.START and last_status == Status.START:
        warnings.warn(f"step {step} was already started", stacklevel=2)
    elif status == Status.END and last_status != Status.START:
        warnings.warn(f"step {step} was not started", stacklevel=2)


def record(
    root: Path,
    step: Step,
    status: Status,
    answers: Mapping[str, str] | None = None,
    timestamp: datetime | None = None,
) -> tuple[Path, Path | None]:
    """Record the start or end of a step + some survey answers.

    Call ``check_status`` first to warn about steps started twice or ended without
    being started. Returns the paths to the timestamps file and to the survey file
    (if applicable).
    """
    answers = answers or {}
    questions = _check_answers(step, status, answers)

    dpath = root / BRAINFLEX_DIRNAME
    fpath_timestamps = dpath / TIMESTAMPS_FILENAME
    timestamp = timestamp or datetime.now()
    if timestamp.tzinfo is None:
        timestamp = timestamp.astimezone()  # naive -> interpret as local time
    row = {
        COL_TIMESTAMP: timestamp.isoformat(timespec="seconds"),
        COL_STEP: str(step),
        COL_STATUS: str(status),
    }
    append_tsv(fpath_timestamps, TIMESTAMPS_COLUMNS, [row])

    if not questions:
        return fpath_timestamps, None

    fpath_survey = dpath / STEP_SURVEY_FILENAME
    append_tsv(
        fpath_survey,
        STEP_SURVEY_COLUMNS,
        (
            {
                COL_STEP: str(step),
                COL_QUESTION: q,
                COL_ANSWER: answers[q],
            }
            for q in questions
        ),
    )
    return fpath_timestamps, fpath_survey
