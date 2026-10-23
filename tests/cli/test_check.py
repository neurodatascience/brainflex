from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from brainflex.cli.main import app
from brainflex.core.check import CheckResult


@pytest.fixture
def mock_check(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("brainflex.cli.check.check")


class TestCheck:
    def test_path(self, runner: CliRunner, mock_check: MagicMock, tmp_path: Path):
        mock_check.return_value = []
        result = runner.invoke(app, ["check", str(tmp_path)])
        assert result.exit_code == 0
        mock_check.assert_called_once_with(tmp_path.resolve())

    def test_default_path(
        self,
        runner: CliRunner,
        mock_check: MagicMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(tmp_path)
        mock_check.return_value = []
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 0
        mock_check.assert_called_once_with(tmp_path.resolve())

    def test_all_passed(self, runner: CliRunner, mock_check: MagicMock):
        mock_check.return_value = [CheckResult("Docker", True, "found")]
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 0
        assert "[OK] Docker: found" in result.stdout

    def test_warning(self, runner: CliRunner, mock_check: MagicMock):
        mock_check.return_value = [
            CheckResult("Docker", True, "found"),
            CheckResult("OS", False, "detected Darwin", required=False),
        ]
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 0
        assert "[WARN] OS: detected Darwin" in result.stdout

    def test_failure(self, runner: CliRunner, mock_check: MagicMock):
        mock_check.return_value = [
            CheckResult("Docker", False, "not found"),
            CheckResult("OS", True, "detected Linux", required=False),
        ]
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 1
        assert "[FAIL] Docker: not found" in result.stdout
        assert "[OK] OS: detected Linux" in result.stdout
