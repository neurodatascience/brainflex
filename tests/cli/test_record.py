from pathlib import Path
from unittest.mock import ANY, MagicMock

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


FPATH_TIMESTAMPS = Path("timestamps.tsv")
FPATH_SURVEY = Path("step_survey.tsv")


def _fake_record(*args, answers: dict[str, str], **kwargs) -> tuple[Path, Path | None]:
    return FPATH_TIMESTAMPS, FPATH_SURVEY if answers else None


@pytest.fixture
def mock_record(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("brainflex.cli.record.record", side_effect=_fake_record)


class TestRecord:
    def test_start(self, runner: CliRunner, mock_record: MagicMock, dpath_root: Path):
        result = runner.invoke(
            app, ["record", "idp_extraction", "start", "--project", str(dpath_root)]
        )
        assert result.exit_code == 0
        assert "?" not in result.stdout
        assert (
            f"Saved timestamp for (idp_extraction, start) to {FPATH_TIMESTAMPS}"
            in result.stdout
        )
        assert "Saved answers" not in result.stdout
        mock_record.assert_called_once_with(
            dpath_root.resolve(),
            Step.IDP_EXTRACTION,
            Status.START,
            answers={},
            timestamp=ANY,
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
        assert (
            f"Saved timestamp for (fedbiomed_node_part_1, end) to {FPATH_TIMESTAMPS}"
            in result.stdout
        )
        assert f"Saved answers to {FPATH_SURVEY}" in result.stdout
        mock_record.assert_called_once_with(
            dpath_root.resolve(),
            Step.FEDBIOMED_NODE_PART_1,
            Status.END,
            answers={QUESTION_NOTES: notes},
            timestamp=ANY,
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
            input="yes\n1-4h\nwent fine\n",
        )
        assert result.exit_code == 0
        stdout = _unwrap(result.stdout)
        # questions are asked in order, with the free-form question last
        assert (
            stdout.index(QUESTION_TOOLS_EASIER)
            < stdout.index(QUESTION_TIME_WITHOUT_TOOLS)
            < stdout.index(QUESTION_NOTES)
        )
        assert "[yes/no/unsure]" in stdout
        assert (
            f"Saved timestamp for ({step}, end) to {FPATH_TIMESTAMPS}" in result.stdout
        )
        assert f"Saved answers to {FPATH_SURVEY}" in result.stdout
        mock_record.assert_called_once_with(
            dpath_root.resolve(),
            step,
            Status.END,
            answers={
                QUESTION_TOOLS_EASIER: "yes",
                QUESTION_TIME_WITHOUT_TOOLS: "1-4h",
                QUESTION_NOTES: "went fine",
            },
            timestamp=ANY,
        )

    def test_end_data_prep_invalid_input_reprompts(
        self, runner: CliRunner, mock_record: MagicMock, dpath_root: Path
    ):
        result = runner.invoke(
            app,
            ["record", "idp_extraction", "end", "--project", str(dpath_root)],
            input="maybe\nunsure\n2 days\n>7d\n\n",
        )
        assert result.exit_code == 0
        mock_record.assert_called_once_with(
            dpath_root.resolve(),
            Step.IDP_EXTRACTION,
            Status.END,
            answers={
                QUESTION_TOOLS_EASIER: "unsure",
                QUESTION_TIME_WITHOUT_TOOLS: ">7d",
                QUESTION_NOTES: "",
            },
            timestamp=ANY,
        )

    def test_timestamp_before_prompts(
        self,
        runner: CliRunner,
        mock_record: MagicMock,
        dpath_root: Path,
        mocker: MockerFixture,
    ):
        manager = MagicMock()
        mock_datetime = mocker.patch("brainflex.cli.record.datetime")
        mock_ask = mocker.patch("brainflex.cli.record.Prompt.ask", return_value="")
        manager.attach_mock(mock_datetime.now, "now")
        manager.attach_mock(mock_ask, "ask")
        result = runner.invoke(
            app,
            ["record", "fedbiomed_node_part_1", "end", "--project", str(dpath_root)],
        )
        assert result.exit_code == 0
        names = [name for name, *_ in manager.mock_calls]
        assert names.index("now") < names.index("ask")
        assert (
            mock_record.call_args.kwargs["timestamp"]
            is mock_datetime.now.return_value.astimezone.return_value
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
            dpath_root.resolve(),
            Step.IDP_EXTRACTION,
            Status.START,
            answers={},
            timestamp=ANY,
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
            dpath_root.resolve(),
            Step.IDP_EXTRACTION,
            Status.START,
            answers={},
            timestamp=ANY,
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

    def test_warning_already_started(
        self, runner: CliRunner, mock_record: MagicMock, dpath_root: Path
    ):
        args = ["record", "idp_extraction", "start", "--project", str(dpath_root)]
        mock_record.side_effect = None
        (dpath_root / BRAINFLEX_DIRNAME / TIMESTAMPS_FILENAME).write_text(
            "timestamp\tstep\tstatus\nt0\tidp_extraction\tstart\n"
        )
        mock_record.return_value = (FPATH_TIMESTAMPS, None)
        result = runner.invoke(app, args)
        assert result.exit_code == 0
        assert "WARNING: step idp_extraction was already started" in result.stderr

    @pytest.mark.parametrize("step", ["idp_extraction", "fedbiomed_node_part_1"])
    def test_warning_not_started_printed_first(
        self, runner: CliRunner, mock_record: MagicMock, dpath_root: Path, step: str
    ):
        result = runner.invoke(
            app,
            ["record", step, "end", "--project", str(dpath_root)],
            input="yes\n1-4h\n\n",
        )
        assert result.exit_code == 0
        assert result.output.startswith(f"WARNING: step {step} was not started\n")
        mock_record.assert_called_once()

    def test_end_to_end(self, runner: CliRunner, dpath_root: Path):
        args = ["record", "fl_ready_data", "--project", str(dpath_root)]
        args_start = [*args[:2], "start", *args[2:]]
        args_end = [*args[:2], "end", *args[2:]]
        dpath = dpath_root.resolve() / BRAINFLEX_DIRNAME
        result = runner.invoke(app, args_start)
        assert result.exit_code == 0
        fpath_timestamps = dpath / TIMESTAMPS_FILENAME
        assert (
            f"Saved timestamp for (fl_ready_data, start) to {fpath_timestamps}"
            in result.stdout
        )
        assert "Saved answers" not in result.stdout
        result = runner.invoke(app, args_end, input="yes\n<1h\nok\n")
        assert "WARNING" not in result.stderr
        assert result.exit_code == 0
        assert (
            f"Saved timestamp for (fl_ready_data, end) to {fpath_timestamps}"
            in result.stdout
        )
        assert f"Saved answers to {dpath / STEP_SURVEY_FILENAME}" in result.stdout
        df_timestamps = pd.read_csv(dpath / TIMESTAMPS_FILENAME, sep="\t", dtype=str)
        assert list(df_timestamps.columns) == ["timestamp", "step", "status"]
        assert list(df_timestamps["status"]) == ["start", "end"]
        assert (dpath / STEP_SURVEY_FILENAME).read_text().splitlines() == [
            "step\tquestion\tanswer",
            f"fl_ready_data\t{QUESTION_TOOLS_EASIER}\tyes",
            f"fl_ready_data\t{QUESTION_TIME_WITHOUT_TOOLS}\t<1h",
            f"fl_ready_data\t{QUESTION_NOTES}\tok",
        ]
