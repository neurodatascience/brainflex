from pathlib import Path

import pytest
from typer.testing import CliRunner

from brainflex.utils.constants import BRAINFLEX_DIRNAME, DATA_DIRNAME


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def dpath_subdir(tmp_path: Path) -> Path:
    """Subdirectory of a project initialized in ``tmp_path``."""
    (tmp_path / BRAINFLEX_DIRNAME).mkdir()
    dpath = tmp_path / DATA_DIRNAME / "ds000001"
    dpath.mkdir(parents=True)
    return dpath
