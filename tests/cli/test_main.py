import importlib

import pytest
from typer.testing import CliRunner

from brainflex import __version__
from brainflex.cli.main import app

COMMAND_NAMES = [command.name for command in app.registered_commands]


class TestMain:
    def test_version(self, runner: CliRunner):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert result.stdout.strip() == __version__


class TestCommandLayout:
    @pytest.mark.parametrize("name", COMMAND_NAMES)
    def test_command_layout(self, name: str):
        # each CLI command maps to cli/<name>.py:<name>_cli and core/<name>.py:<name>
        cli_module = importlib.import_module(f"brainflex.cli.{name}")
        core_module = importlib.import_module(f"brainflex.core.{name}")
        command = next(c for c in app.registered_commands if c.name == name)
        assert command.callback is getattr(cli_module, f"{name}_cli")
        assert callable(getattr(core_module, name))
