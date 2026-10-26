from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from brainflex.cli.main import app
from brainflex.core.record import Status, Step


@pytest.fixture
def mock_record(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("brainflex.cli.record.record")


class TestRecord:
    def test_start(self, runner: CliRunner, mock_record: MagicMock, tmp_path: Path):
        result = runner.invoke(app, ["record", "get-data", "start", str(tmp_path)])
        assert result.exit_code == 0
        assert "Notes" not in result.stdout
        assert "Recorded get-data start" in result.stdout
        mock_record.assert_called_once_with(
            tmp_path.resolve(), Step.GET_DATA, Status.START, notes=""
        )

    @pytest.mark.parametrize(
        ("user_input", "notes"), [("went fine\n", "went fine"), ("\n", "")]
    )
    def test_end(
        self,
        runner: CliRunner,
        mock_record: MagicMock,
        tmp_path: Path,
        user_input: str,
        notes: str,
    ):
        result = runner.invoke(
            app, ["record", "get-data", "end", str(tmp_path)], input=user_input
        )
        assert result.exit_code == 0
        assert "Notes" in result.stdout
        mock_record.assert_called_once_with(
            tmp_path.resolve(), Step.GET_DATA, Status.END, notes=notes
        )

    def test_default_path(
        self,
        runner: CliRunner,
        mock_record: MagicMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["record", "get-data", "start"])
        assert result.exit_code == 0
        mock_record.assert_called_once_with(
            tmp_path.resolve(), Step.GET_DATA, Status.START, notes=""
        )

    @pytest.mark.parametrize("explicit", [True, False])
    def test_subdirectory(
        self,
        runner: CliRunner,
        mock_record: MagicMock,
        tmp_path: Path,
        dpath_subdir: Path,
        monkeypatch: pytest.MonkeyPatch,
        explicit: bool,
    ):
        monkeypatch.chdir(dpath_subdir)
        result = runner.invoke(
            app,
            ["record", "get-data", "start", *([str(dpath_subdir)] if explicit else [])],
        )
        assert result.exit_code == 0
        mock_record.assert_called_once_with(
            tmp_path.resolve(), Step.GET_DATA, Status.START, notes=""
        )

    @pytest.mark.parametrize(
        "args", [["bad-step", "start"], ["get-data", "bad-status"]]
    )
    def test_invalid_choice(
        self, runner: CliRunner, mock_record: MagicMock, args: list[str]
    ):
        result = runner.invoke(app, ["record", *args])
        assert result.exit_code == 2
        mock_record.assert_not_called()

    def test_not_initialized(
        self, runner: CliRunner, mock_record: MagicMock, tmp_path: Path
    ):
        mock_record.side_effect = FileNotFoundError("Project not initialized")
        result = runner.invoke(app, ["record", "get-data", "start", str(tmp_path)])
        assert result.exit_code == 1
        assert "not initialized" in result.stderr
        assert "brainflex init" in result.stderr
