"""Project initialization."""

from pathlib import Path

from brainflex.utils.constants import BRAINFLEX_DIRNAME, DATA_DIRNAME


def init(root: Path) -> None:
    """Initialize the project directory.

    Raises FileExistsError if the project has already been initialized.
    """
    dpath_brainflex = root / BRAINFLEX_DIRNAME
    if dpath_brainflex.exists():
        raise FileExistsError(f"Project already initialized: {dpath_brainflex} exists")

    (root / DATA_DIRNAME).mkdir(parents=True, exist_ok=True)
    dpath_brainflex.mkdir(parents=True)
