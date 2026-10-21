"""Project initialization."""

from pathlib import Path

from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    DATA_DIRNAME,
    STATUS_LOG_COLUMNS,
    STATUS_LOG_FILENAME,
)


def init(root: Path) -> None:
    """Initialize the project directory.

    Raises FileExistsError if the status log file already exists.
    """
    status_log = root / BRAINFLEX_DIRNAME / STATUS_LOG_FILENAME
    if status_log.exists():
        raise FileExistsError(f"Project already initialized: {status_log} exists")

    (root / DATA_DIRNAME).mkdir(parents=True, exist_ok=True)
    status_log.parent.mkdir(parents=True, exist_ok=True)
    status_log.write_text("\t".join(STATUS_LOG_COLUMNS) + "\n")
