import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest

from brainflex.core.record import (
    DATA_PREP_STEPS,
    Status,
    Step,
    check_status,
    get_step_questions,
    record,
)
from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    QUESTION_NOTES,
    QUESTION_TIME_WITHOUT_TOOLS,
    QUESTION_TOOLS_EASIER,
    STEP_SURVEY_COLUMNS,
    STEP_SURVEY_FILENAME,
    TIMESTAMPS_COLUMNS,
    TIMESTAMPS_FILENAME,
)

DATA_PREP_ANSWERS = {
    QUESTION_TOOLS_EASIER: "yes",
    QUESTION_TIME_WITHOUT_TOOLS: "1-4h",
    QUESTION_NOTES: "went fine",
}


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / BRAINFLEX_DIRNAME).mkdir()
    return tmp_path


@pytest.fixture
def fpath_timestamps(root: Path) -> Path:
    return root / BRAINFLEX_DIRNAME / TIMESTAMPS_FILENAME


@pytest.fixture
def fpath_survey(root: Path) -> Path:
    return root / BRAINFLEX_DIRNAME / STEP_SURVEY_FILENAME


def _read(fpath: Path) -> pd.DataFrame:
    return pd.read_csv(fpath, sep="\t", dtype=str, keep_default_na=False)


class TestGetStepQuestions:
    @pytest.mark.parametrize("step", sorted(DATA_PREP_STEPS))
    def test_data_prep(self, step: Step):
        assert list(get_step_questions(step)) == [
            QUESTION_TOOLS_EASIER,
            QUESTION_TIME_WITHOUT_TOOLS,
            QUESTION_NOTES,
        ]

    @pytest.mark.parametrize("step", sorted(set(Step) - DATA_PREP_STEPS))
    def test_other(self, step: Step):
        assert list(get_step_questions(step)) == [QUESTION_NOTES]


class TestRecord:
    def test_start(self, root: Path, fpath_timestamps: Path, fpath_survey: Path):
        assert record(root, Step.IDP_EXTRACTION, Status.START) == (
            fpath_timestamps,
            None,
        )
        df = _read(fpath_timestamps)
        assert tuple(df.columns) == TIMESTAMPS_COLUMNS
        assert len(df) == 1
        row = df.iloc[0]
        assert row["step"] == "idp_extraction"
        assert row["status"] == "start"
        assert datetime.fromisoformat(row["timestamp"]).tzinfo is not None
        assert not fpath_survey.exists()

    def test_timestamp(self, root: Path, fpath_timestamps: Path):
        timestamp = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=-5)))
        record(root, Step.IDP_EXTRACTION, Status.START, timestamp=timestamp)
        assert _read(fpath_timestamps)["timestamp"].iloc[0] == (
            "2026-01-02T03:04:05-05:00"
        )

    def test_end_data_prep(
        self, root: Path, fpath_timestamps: Path, fpath_survey: Path
    ):
        record(root, Step.IDP_EXTRACTION, Status.START)
        assert record(
            root, Step.IDP_EXTRACTION, Status.END, answers=DATA_PREP_ANSWERS
        ) == (fpath_timestamps, fpath_survey)
        assert list(_read(fpath_timestamps)["status"]) == ["start", "end"]
        assert fpath_timestamps.read_text().count("timestamp") == 1
        df = _read(fpath_survey)
        assert tuple(df.columns) == STEP_SURVEY_COLUMNS
        assert df.to_dict("records") == [
            {
                "step": "idp_extraction",
                "question": QUESTION_TOOLS_EASIER,
                "answer": "yes",
            },
            {
                "step": "idp_extraction",
                "question": QUESTION_TIME_WITHOUT_TOOLS,
                "answer": "1-4h",
            },
            {
                "step": "idp_extraction",
                "question": QUESTION_NOTES,
                "answer": "went fine",
            },
        ]

    def test_end_other(self, root: Path, fpath_timestamps: Path, fpath_survey: Path):
        record(root, Step.FEDBIOMED_NODE_PART_1, Status.START)
        assert record(
            root, Step.FEDBIOMED_NODE_PART_1, Status.END, answers={QUESTION_NOTES: ""}
        ) == (fpath_timestamps, fpath_survey)
        assert _read(fpath_survey).to_dict("records") == [
            {"step": "fedbiomed_node_part_1", "question": QUESTION_NOTES, "answer": ""}
        ]

    def test_survey_appends_in_question_order(self, root: Path, fpath_survey: Path):
        record(root, Step.FL_READY_DATA, Status.START)
        record(
            root,
            Step.FL_READY_DATA,
            Status.END,
            answers=dict(reversed(DATA_PREP_ANSWERS.items())),
        )
        record(root, Step.FEDBIOMED_NODE_PART_2, Status.START)
        record(
            root, Step.FEDBIOMED_NODE_PART_2, Status.END, answers={QUESTION_NOTES: "x"}
        )
        df = _read(fpath_survey)
        assert list(df["question"]) == [*DATA_PREP_ANSWERS, QUESTION_NOTES]
        assert fpath_survey.read_text().count("question") == 1

    def test_notes_with_special_characters(self, root: Path, fpath_survey: Path):
        notes = 'tab\there\nnew line and "quotes"'
        record(root, Step.FEDBIOMED_NODE_PART_1, Status.START)
        record(
            root,
            Step.FEDBIOMED_NODE_PART_1,
            Status.END,
            answers={QUESTION_NOTES: notes},
        )
        assert _read(fpath_survey).iloc[-1]["answer"] == notes

    @pytest.mark.parametrize(
        ("step", "status", "answers"),
        [
            (Step.IDP_EXTRACTION, Status.START, {QUESTION_NOTES: ""}),
            (Step.IDP_EXTRACTION, Status.END, None),
            (Step.IDP_EXTRACTION, Status.END, {QUESTION_NOTES: ""}),
            (Step.FEDBIOMED_NODE_PART_1, Status.END, DATA_PREP_ANSWERS),
            (Step.FEDBIOMED_NODE_PART_1, Status.END, {"Unknown?": ""}),
        ],
    )
    def test_invalid_questions(
        self,
        root: Path,
        fpath_timestamps: Path,
        fpath_survey: Path,
        step: Step,
        status: Status,
        answers: dict[str, str] | None,
    ):
        with pytest.raises(ValueError, match="exactly these questions"):
            record(root, step, status, answers=answers)
        assert not fpath_timestamps.exists()
        assert not fpath_survey.exists()

    @pytest.mark.parametrize(
        ("question", "answer"),
        [
            (QUESTION_TOOLS_EASIER, "maybe"),
            (QUESTION_TOOLS_EASIER, "4"),
            (QUESTION_TIME_WITHOUT_TOOLS, "2 days"),
        ],
    )
    def test_invalid_answer(
        self, root: Path, fpath_timestamps: Path, question: str, answer: str
    ):
        with pytest.raises(ValueError, match="must be one of"):
            record(
                root,
                Step.SEMANTIC_HARMONIZATION,
                Status.END,
                answers={**DATA_PREP_ANSWERS, question: answer},
            )
        assert not fpath_timestamps.exists()

    def test_no_warning(self, root: Path):
        # warnings are emitted by check_status
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            record(
                root,
                Step.FEDBIOMED_NODE_PART_1,
                Status.END,
                answers={QUESTION_NOTES: ""},
            )
            record(root, Step.FEDBIOMED_NODE_PART_1, Status.START)
            record(root, Step.FEDBIOMED_NODE_PART_1, Status.START)

    def test_invalid_timestamps_file(self, root: Path, fpath_timestamps: Path):
        fpath_timestamps.write_text("timestamp\tstep\nt0\tidp_extraction\n")
        with pytest.warns(UserWarning, match="invalid file"):
            record(root, Step.IDP_EXTRACTION, Status.START)
        assert len(list(fpath_timestamps.parent.glob("timestamps-*.tsv"))) == 1
        assert len(_read(fpath_timestamps)) == 1


class TestCheckStatus:
    def _record(self, root: Path, step: Step, status: Status) -> None:
        answers = {QUESTION_NOTES: ""} if status == Status.END else None
        record(root, step, status, answers=answers)

    @pytest.mark.parametrize(
        ("statuses", "status"),
        [
            ([], Status.START),
            ([Status.START], Status.END),
            ([Status.START, Status.END], Status.START),
        ],
    )
    def test_no_warning(self, root: Path, statuses: list[Status], status: Status):
        for previous in statuses:
            self._record(root, Step.FEDBIOMED_NODE_PART_1, previous)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            check_status(root, Step.FEDBIOMED_NODE_PART_1, status)

    @pytest.mark.parametrize(
        ("statuses", "status", "message"),
        [
            ([], Status.END, "was not started"),
            ([Status.START], Status.START, "was already started"),
            ([Status.START, Status.END], Status.END, "was not started"),
        ],
    )
    def test_warning(
        self,
        root: Path,
        fpath_timestamps: Path,
        statuses: list[Status],
        status: Status,
        message: str,
    ):
        for previous in statuses:
            self._record(root, Step.FEDBIOMED_NODE_PART_1, previous)
        content = fpath_timestamps.read_text() if statuses else None
        with pytest.warns(UserWarning, match=message):
            check_status(root, Step.FEDBIOMED_NODE_PART_1, status)
        # nothing is written
        if content is None:
            assert not fpath_timestamps.exists()
        else:
            assert fpath_timestamps.read_text() == content

    def test_other_step(self, root: Path):
        self._record(root, Step.IDP_EXTRACTION, Status.START)
        with pytest.warns(UserWarning, match="fl_ready_data was not started"):
            check_status(root, Step.FL_READY_DATA, Status.END)

    def test_invalid_timestamps_file(self, root: Path, fpath_timestamps: Path):
        fpath_timestamps.write_text("timestamp\tstep\nt0\tidp_extraction\n")
        with pytest.warns(UserWarning) as record_warnings:
            check_status(root, Step.IDP_EXTRACTION, Status.START)
        # previous records are discarded, so no start/end warning
        assert str(record_warnings[0].message).startswith("invalid file")
        assert len(record_warnings) == 1
