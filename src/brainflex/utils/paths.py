"""Path utilities."""

from pathlib import Path

from brainflex.utils.constants import BRAINFLEX_DIRNAME


def find_root(path: Path) -> Path:
    """Return the closest of ``path`` and its parents containing the brainflex directory.

    Raises FileNotFoundError if no such directory is found.
    """
    for dpath in (path, *path.parents):
        if (dpath / BRAINFLEX_DIRNAME).is_dir():
            return dpath
    raise FileNotFoundError(
        "Project root directory not found. "
        "Pass --project or run command inside the project."
    )
