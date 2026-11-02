from pathlib import Path

import pytest
from typer.testing import CliRunner

from brainflex.utils.constants import BRAINFLEX_DIRNAME, NIPOPPY_STUDY_DIRNAME


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def dpath_root(tmp_path: Path) -> Path:
    """Root of a project initialized in ``tmp_path``."""
    (tmp_path / BRAINFLEX_DIRNAME).mkdir()
    return tmp_path


@pytest.fixture
def dpath_subdir(dpath_root: Path) -> Path:
    """Subdirectory of a project initialized in ``dpath_root``."""
    dpath = dpath_root / NIPOPPY_STUDY_DIRNAME
    dpath.mkdir(parents=True)
    return dpath
