import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from brainflex.cli.main import app


@pytest.fixture
def mock_get_data(mocker: MockerFixture, tmp_path: Path) -> MagicMock:
    return mocker.patch(
        "brainflex.cli.get_data.get_data", return_value=tmp_path / "data" / "ds000001"
    )


class TestGetData:
    def test_get_data(
        self, runner: CliRunner, mock_get_data: MagicMock, tmp_path: Path
    ):
        result = runner.invoke(app, ["get-data", "ds000001", str(tmp_path)])
        assert result.exit_code == 0
        assert "Downloaded ds000001" in result.stdout
        mock_get_data.assert_called_once_with(
            tmp_path.resolve(),
            "ds000001",
            overwrite=False,
            full_rawbids=False,
            full_freesurfer=False,
        )

    def test_default_path(
        self,
        runner: CliRunner,
        mock_get_data: MagicMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["get-data", "ds000001"])
        assert result.exit_code == 0
        mock_get_data.assert_called_once_with(
            tmp_path.resolve(),
            "ds000001",
            overwrite=False,
            full_rawbids=False,
            full_freesurfer=False,
        )

    @pytest.mark.parametrize("flag", ["--overwrite", "--force", "-f"])
    def test_overwrite(
        self, runner: CliRunner, mock_get_data: MagicMock, tmp_path: Path, flag: str
    ):
        result = runner.invoke(app, ["get-data", "ds000001", str(tmp_path), flag])
        assert result.exit_code == 0
        mock_get_data.assert_called_once_with(
            tmp_path.resolve(),
            "ds000001",
            overwrite=True,
            full_rawbids=False,
            full_freesurfer=False,
        )

    @pytest.mark.parametrize(
        ("flag", "kwarg"),
        [("--full-rawbids", "full_rawbids"), ("--full-freesurfer", "full_freesurfer")],
    )
    def test_full(
        self,
        runner: CliRunner,
        mock_get_data: MagicMock,
        tmp_path: Path,
        flag: str,
        kwarg: str,
    ):
        result = runner.invoke(app, ["get-data", "ds000001", str(tmp_path), flag])
        assert result.exit_code == 0
        assert mock_get_data.call_args.kwargs[kwarg] is True

    def test_already_exists(
        self, runner: CliRunner, mock_get_data: MagicMock, tmp_path: Path
    ):
        mock_get_data.side_effect = FileExistsError("Dataset already exists")
        result = runner.invoke(app, ["get-data", "ds000001", str(tmp_path)])
        assert result.exit_code == 1
        assert "already exists" in result.stderr
        assert "--overwrite" in result.stderr

    @pytest.mark.parametrize(
        ("error", "message"),
        [
            (ValueError("Dataset not found"), "not found"),
            (subprocess.CalledProcessError(1, "nipoppy"), "nipoppy"),
        ],
    )
    def test_error(
        self,
        runner: CliRunner,
        mock_get_data: MagicMock,
        tmp_path: Path,
        error: Exception,
        message: str,
    ):
        mock_get_data.side_effect = error
        result = runner.invoke(app, ["get-data", "ds000001", str(tmp_path)])
        assert result.exit_code == 1
        assert message in result.stderr
