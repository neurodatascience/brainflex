from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from brainflex.cli.main import app


class TestRootOption:
    @pytest.mark.parametrize(
        ("args", "target"),
        [
            (["check"], "brainflex.cli.check.check"),
            (["get-data", "ds000001"], "brainflex.cli.get_data.get_data"),
            (["init", "config.env"], "brainflex.cli.init.init"),
            (["record", "get-data", "start"], "brainflex.cli.record.record"),
        ],
    )
    @pytest.mark.parametrize("explicit", [True, False])
    def test_not_found(
        self,
        runner: CliRunner,
        mocker: MockerFixture,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        args: list[str],
        target: str,
        explicit: bool,
    ):
        monkeypatch.chdir(tmp_path)
        mock_command = mocker.patch(target)
        result = runner.invoke(
            app, [*args, *(["--project", str(tmp_path)] if explicit else [])]
        )
        assert result.exit_code == 2
        assert "Project root directory not found" in result.stderr
        mock_command.assert_not_called()
