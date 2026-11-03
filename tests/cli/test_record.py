import warnings
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from brainflex.cli.main import app
from brainflex.core.record import Status, Step
from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    QUESTION_NOTES,
    QUESTION_TIME_WITHOUT_TOOLS,
    QUESTION_TOOLS_EASIER,
    STEP_SURVEY_FILENAME,
    TIMESTAMPS_FILENAME,
)


def _unwrap(text: str) -> str:
    """Collapse whitespace so that prompts wrapped by rich can be matched."""
    return " ".join(text.split())


@pytest.fixture
def mock_record(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("brainflex.cli.record.record")


class TestRecord:
    def test_start(self, runner: CliRunner, mock_record: MagicMock, dpath_root: Path):
        result = runner.invoke(
            app, ["record", "idp_extraction", "start", "--project", str(dpath_root)]
        )
        assert result.exit_code == 0
        assert "?" not in result.stdout
        assert "Recorded idp_extraction start" in result.stdout
        mock_record.assert_called_once_with(
            dpath_root.resolve(), Step.IDP_EXTRACTION, Status.START, answers={}
        )

    @pytest.mark.parametrize(
        ("user_input", "notes"), [("went fine\n", "went fine"), ("\n", "")]
    )
    def test_end_other(
        self,
        runner: CliRunner,
        mock_record: MagicMock,
        dpath_root: Path,
        user_input: str,
        notes: str,
    ):
        result = runner.invoke(
            app,
            ["record", "fedbiomed_node_part_1", "end", "--project", str(dpath_root)],
            input=user_input,
        )
        assert result.exit_code == 0
        stdout = _unwrap(result.stdout)
        assert QUESTION_NOTES in stdout
        assert QUESTION_TOOLS_EASIER not in stdout
        assert QUESTION_TIME_WITHOUT_TOOLS not in stdout
        mock_record.assert_called_once_with(
            dpath_root.resolve(),
            Step.FEDBIOMED_NODE_PART_1,
            Status.END,
            answers={QUESTION_NOTES: notes},
        )

    @pytest.mark.parametrize(
        "step", [Step.IDP_EXTRACTION, Step.SEMANTIC_HARMONIZATION, Step.FL_READY_DATA]
    )
    def test_end_data_prep(
        self, runner: CliRunner, mock_record: MagicMock, dpath_root: Path, step: Step
    ):
        result = runner.invoke(
            app,
            ["record", str(step), "end", "--project", str(dpath_root)],
            input="4\n1-4h\nwent fine\n",
        )
        assert result.exit_code == 0
        stdout = _unwrap(result.stdout)
        # questions are asked in order, with the free-form question last
        assert (
            stdout.index(QUESTION_TOOLS_EASIER)
            < stdout.index(QUESTION_TIME_WITHOUT_TOOLS)
            < stdout.index(QUESTION_NOTES)
        )
        mock_record.assert_called_once_with(
            dpath_root.resolve(),
            step,
            Status.END,
            answers={
                QUESTION_TOOLS_EASIER: "4",
                QUESTION_TIME_WITHOUT_TOOLS: "1-4h",
                QUESTION_NOTES: "went fine",
            },
        )

    def test_end_data_prep_invalid_input_reprompts(
        self, runner: CliRunner, mock_record: MagicMock, dpath_root: Path
    ):
        result = runner.invoke(
            app,
            ["record", "idp_extraction", "end", "--project", str(dpath_root)],
            input="6\n5\n2 days\n>7d\n\n",
        )
        assert result.exit_code == 0
        mock_record.assert_called_once_with(
            dpath_root.resolve(),
            Step.IDP_EXTRACTION,
            Status.END,
            answers={
                QUESTION_TOOLS_EASIER: "5",
                QUESTION_TIME_WITHOUT_TOOLS: ">7d",
                QUESTION_NOTES: "",
            },
        )

    def test_default_path(
        self,
        runner: CliRunner,
        mock_record: MagicMock,
        dpath_root: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(dpath_root)
        result = runner.invoke(app, ["record", "idp_extraction", "start"])
        assert result.exit_code == 0
        mock_record.assert_called_once_with(
            dpath_root.resolve(), Step.IDP_EXTRACTION, Status.START, answers={}
        )

    @pytest.mark.parametrize("explicit", [True, False])
    def test_subdirectory(
        self,
        runner: CliRunner,
        mock_record: MagicMock,
        dpath_root: Path,
        dpath_subdir: Path,
        monkeypatch: pytest.MonkeyPatch,
        explicit: bool,
    ):
        monkeypatch.chdir(dpath_subdir)
        result = runner.invoke(
            app,
            [
                "record",
                "idp_extraction",
                "start",
                *(["--project", str(dpath_subdir)] if explicit else []),
            ],
        )
        assert result.exit_code == 0
        mock_record.assert_called_once_with(
            dpath_root.resolve(), Step.IDP_EXTRACTION, Status.START, answers={}
        )

    @pytest.mark.parametrize(
        "args",
        [["get-data", "start"], ["bad-step", "start"], ["idp_extraction", "bad"]],
    )
    def test_invalid_choice(
        self, runner: CliRunner, mock_record: MagicMock, args: list[str]
    ):
        result = runner.invoke(app, ["record", *args])
        assert result.exit_code == 2
        mock_record.assert_not_called()

    def test_warning(self, runner: CliRunner, mock_record: MagicMock, dpath_root: Path):
        mock_record.side_effect = lambda *args, **kwargs: warnings.warn(
            "step idp_extraction was already started", stacklevel=2
        )
        result = runner.invoke(
            app, ["record", "idp_extraction", "start", "--project", str(dpath_root)]
        )
        assert result.exit_code == 0
        assert "WARNING: step idp_extraction was already started" in result.stderr

    def test_end_to_end(self, runner: CliRunner, dpath_root: Path):
        args = ["record", "fl_ready_data", "--project", str(dpath_root)]
        args_start = [*args[:2], "start", *args[2:]]
        args_end = [*args[:2], "end", *args[2:]]
        assert runner.invoke(app, args_start).exit_code == 0
        assert runner.invoke(app, args_end, input="3\n<1h\nok\n").exit_code == 0
        dpath = dpath_root / BRAINFLEX_DIRNAME
        df_timestamps = pd.read_csv(dpath / TIMESTAMPS_FILENAME, sep="\t", dtype=str)
        assert list(df_timestamps.columns) == ["timestamp", "step", "status"]
        assert list(df_timestamps["status"]) == ["start", "end"]
        assert (dpath / STEP_SURVEY_FILENAME).read_text().splitlines() == [
            "step\tquestion\tanswer",
            f"fl_ready_data\t{QUESTION_TOOLS_EASIER}\t3",
            f"fl_ready_data\t{QUESTION_TIME_WITHOUT_TOOLS}\t<1h",
            f"fl_ready_data\t{QUESTION_NOTES}\tok",
        ]
