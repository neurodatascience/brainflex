"""Prerequisite checks."""

import platform
import subprocess
import urllib.request
from pathlib import Path
from typing import NamedTuple

from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    CHECK_TIMEOUT,
    INTERNET_CHECK_URL,
)


class CheckResult(NamedTuple):
    """Result of a single prerequisite check."""

    name: str
    passed: bool
    message: str
    required: bool = True


def _run(cmd: list[str]) -> subprocess.CompletedProcess | None:
    """Attempt to run a command."""
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=CHECK_TIMEOUT
        )
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None


def _check_os() -> CheckResult:
    system = platform.system()
    return CheckResult(
        "OS", system == "Linux", f"detected {system or 'unknown'}", required=False
    )


def _check_docker() -> CheckResult:
    result = _run(["docker", "--version"])
    if result is None:
        return CheckResult("Docker", False, "docker --version failed")
    return CheckResult("Docker", True, result.stdout.strip())


def _check_docker_daemon() -> CheckResult:
    if _run(["docker", "info"]) is None:
        return CheckResult(
            "Docker daemon",
            False,
            "docker info failed (daemon not running or insufficient permissions)",
        )
    return CheckResult("Docker daemon", True, "Docker daemon is reachable")


def _check_docker_compose() -> CheckResult:
    result = _run(["docker", "compose", "version"])
    if result is None:
        return CheckResult("Docker Compose", False, "docker compose version failed")
    return CheckResult("Docker Compose", True, result.stdout.strip())


def _check_internet() -> CheckResult:
    try:
        with urllib.request.urlopen(INTERNET_CHECK_URL, timeout=CHECK_TIMEOUT):
            pass
    except OSError as e:
        return CheckResult(
            "Internet",
            False,
            f"could not reach {INTERNET_CHECK_URL}: {e}",
            required=False,
        )
    return CheckResult(
        "Internet", True, f"reached {INTERNET_CHECK_URL}", required=False
    )


def _check_project(root: Path) -> CheckResult:
    brainflex_dir_path = root / BRAINFLEX_DIRNAME
    if not brainflex_dir_path.is_dir():
        return CheckResult(
            "Project", False, f"project not initialized: {brainflex_dir_path} not found"
        )
    return CheckResult("Project", True, f"project initialized in {root}")


def check(root: Path) -> list[CheckResult]:
    """Run all prerequisite checks for the project at ``root``."""
    return [
        _check_project(root),
        _check_os(),
        _check_docker(),
        _check_docker_daemon(),
        _check_docker_compose(),
        _check_internet(),
    ]
