from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from brainflex.cli.main import app


@pytest.fixture
def mock_init(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("brainflex.cli.init.init")


@pytest.fixture
def fpath_vpn_config(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("download") / "config.env"


class TestInit:
    def test_init(
        self,
        runner: CliRunner,
        mock_init: MagicMock,
        dpath_root: Path,
        fpath_vpn_config: Path,
    ):
        result = runner.invoke(
            app, ["init", str(fpath_vpn_config), "--project", str(dpath_root)]
        )
        assert result.exit_code == 0
        assert "Created" in result.stdout
        mock_init.assert_called_once_with(
            dpath_root.resolve(), fpath_vpn_config.resolve()
        )

    def test_init_default_path(
        self,
        runner: CliRunner,
        mock_init: MagicMock,
        dpath_root: Path,
        fpath_vpn_config: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(dpath_root)
        result = runner.invoke(app, ["init", str(fpath_vpn_config)])
        assert result.exit_code == 0
        mock_init.assert_called_once_with(
            dpath_root.resolve(), fpath_vpn_config.resolve()
        )

    @pytest.mark.parametrize("explicit", [True, False])
    def test_init_subdirectory(
        self,
        runner: CliRunner,
        mock_init: MagicMock,
        dpath_root: Path,
        dpath_subdir: Path,
        fpath_vpn_config: Path,
        monkeypatch: pytest.MonkeyPatch,
        explicit: bool,
    ):
        monkeypatch.chdir(dpath_subdir)
        result = runner.invoke(
            app,
            [
                "init",
                str(fpath_vpn_config),
                *(["--project", str(dpath_subdir)] if explicit else []),
            ],
        )
        assert result.exit_code == 0
        mock_init.assert_called_once_with(
            dpath_root.resolve(), fpath_vpn_config.resolve()
        )

    def test_init_relative_vpn_config(
        self,
        runner: CliRunner,
        mock_init: MagicMock,
        dpath_root: Path,
        dpath_subdir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        # relative to the working directory, not the project root
        monkeypatch.chdir(dpath_subdir)
        result = runner.invoke(app, ["init", "config.env"])
        assert result.exit_code == 0
        mock_init.assert_called_once_with(
            dpath_root.resolve(), (dpath_subdir / "config.env").resolve()
        )

    def test_init_missing_vpn_config_argument(
        self, runner: CliRunner, mock_init: MagicMock
    ):
        result = runner.invoke(app, ["init"])
        assert result.exit_code != 0
        mock_init.assert_not_called()

    @pytest.mark.parametrize(
        "error",
        [
            FileExistsError("already initialized"),
            FileNotFoundError("Not a brainflex project"),
        ],
    )
    def test_init_error(
        self,
        runner: CliRunner,
        mock_init: MagicMock,
        dpath_root: Path,
        fpath_vpn_config: Path,
        error: Exception,
    ):
        mock_init.side_effect = error
        result = runner.invoke(
            app, ["init", str(fpath_vpn_config), "--project", str(dpath_root)]
        )
        assert result.exit_code == 1
        assert str(error) in result.stderr
