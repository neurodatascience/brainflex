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

    @pytest.mark.parametrize(
        ("check_results", "return_code", "expected_messages"),
        [
            ([CheckResult("Docker", True, "found")], 0, ["[OK] Docker: found"]),
            (
                [
                    CheckResult("Docker", True, "found"),
                    CheckResult("OS", False, "detected Darwin", required=False),
                ],
                0,
                ["[OK] Docker: found", "[WARN] OS: detected Darwin"],
            ),
            (
                [
                    CheckResult("Docker", False, "not found"),
                    CheckResult("OS", True, "detected Linux", required=False),
                ],
                1,
                [
                    "[FAIL] Docker: not found",
                    "[OK] OS: detected Linux",
                ],
            ),
        ],
    )
    def test_output(
        self,
        check_results,
        return_code,
        expected_messages,
        runner: CliRunner,
        mock_check: MagicMock,
    ):
        mock_check.return_value = check_results
        result = runner.invoke(app, ["check"])
        assert result.exit_code == return_code
        for message in expected_messages:
            assert message in result.stdout
