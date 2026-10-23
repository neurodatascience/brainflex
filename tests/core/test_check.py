import subprocess
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from brainflex.core.check import (
    CheckResult,
    _check_docker,
    _check_docker_compose,
    _check_docker_daemon,
    _check_internet,
    _check_os,
    _check_project,
    check,
)
from brainflex.core.init import init


@pytest.fixture
def mock_run(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("brainflex.core.check.subprocess.run")


class TestCheckProject:
    def test_initialized(self, tmp_path: Path):
        init(tmp_path)
        result = _check_project(tmp_path)
        assert result.passed
        assert result.required

    def test_not_initialized(self, tmp_path: Path):
        result = _check_project(tmp_path)
        assert not result.passed
        assert "not initialized" in result.message


class TestCheckOs:
    def test_linux(self, mocker: MockerFixture):
        mocker.patch("brainflex.core.check.platform.system", return_value="Linux")
        result = _check_os()
        assert result.passed
        assert not result.required

    def test_not_linux(self, mocker: MockerFixture):
        mocker.patch("brainflex.core.check.platform.system", return_value="Darwin")
        result = _check_os()
        assert not result.passed
        assert "Darwin" in result.message


class TestCheckDocker:
    def test_ok(self, mock_run: MagicMock):
        mock_run.return_value.stdout = "Docker version 27.0.0, build abc\n"
        result = _check_docker()
        assert result.passed
        assert result.message == "Docker version 27.0.0, build abc"
        assert mock_run.call_args.args[0] == ["docker", "--version"]

    @pytest.mark.parametrize(
        "error",
        [
            FileNotFoundError(),
            subprocess.CalledProcessError(1, "docker"),
            subprocess.TimeoutExpired("docker", 10),
        ],
    )
    def test_fail(self, mock_run: MagicMock, error: Exception):
        mock_run.side_effect = error
        result = _check_docker()
        assert not result.passed
        assert result.required


class TestCheckDockerDaemon:
    def test_ok(self, mock_run: MagicMock):
        assert _check_docker_daemon().passed
        mock_run.assert_called_once()
        assert mock_run.call_args.args[0] == ["docker", "info"]

    @pytest.mark.parametrize(
        "error",
        [
            FileNotFoundError(),
            subprocess.CalledProcessError(1, "docker"),
            subprocess.TimeoutExpired("docker", 10),
        ],
    )
    def test_fail(self, mock_run: MagicMock, error: Exception):
        mock_run.side_effect = error
        result = _check_docker_daemon()
        assert not result.passed
        assert result.required


class TestCheckDockerCompose:
    def test_ok(self, mock_run: MagicMock):
        mock_run.return_value.stdout = "Docker Compose version v2.0.0\n"
        result = _check_docker_compose()
        assert result.passed
        assert result.message == "Docker Compose version v2.0.0"

    @pytest.mark.parametrize(
        "error",
        [
            FileNotFoundError(),
            subprocess.CalledProcessError(1, "docker"),
            subprocess.TimeoutExpired("docker", 10),
        ],
    )
    def test_fail(self, mock_run: MagicMock, error: Exception):
        mock_run.side_effect = error
        assert not _check_docker_compose().passed


class TestCheckInternet:
    def test_ok(self, mocker: MockerFixture):
        mocker.patch("brainflex.core.check.urllib.request.urlopen")
        result = _check_internet()
        assert result.passed
        assert not result.required

    @pytest.mark.parametrize(
        "error", [urllib.error.URLError("no route"), TimeoutError()]
    )
    def test_fail(self, mocker: MockerFixture, error: Exception):
        mocker.patch("brainflex.core.check.urllib.request.urlopen", side_effect=error)
        result = _check_internet()
        assert not result.passed
        assert not result.required


class TestCheck:
    def test_check(self, mocker: MockerFixture, mock_run: MagicMock, tmp_path: Path):
        mocker.patch("brainflex.core.check.urllib.request.urlopen")
        results = check(tmp_path)
        assert len(results) == 6
        assert all(isinstance(r, CheckResult) for r in results)
