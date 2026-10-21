from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from brainflex.cli.main import app


@pytest.fixture
def mock_init(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("brainflex.cli.init.init")


class TestInit:
    def test_init(self, runner: CliRunner, mock_init: MagicMock, tmp_path: Path):
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert "Initialized project" in result.stdout
        mock_init.assert_called_once_with(tmp_path.resolve())

    def test_init_default_path(
        self,
        runner: CliRunner,
        mock_init: MagicMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        mock_init.assert_called_once_with(tmp_path.resolve())

    def test_init_error(self, runner: CliRunner, mock_init: MagicMock, tmp_path: Path):
        mock_init.side_effect = FileExistsError("already initialized")
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 1
        assert "already initialized" in result.stderr
