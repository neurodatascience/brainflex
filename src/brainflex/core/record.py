"""Record the start and end of experiment steps."""

import warnings
from datetime import datetime
from enum import StrEnum
from pathlib import Path

import pandas as pd

from brainflex.utils.constants import (
    BACKUP_TIMESTAMP_FORMAT,
    BRAINFLEX_DIRNAME,
    COL_NOTES,
    COL_STATUS,
    COL_STEP,
    COL_TIMESTAMP,
    STATUS_LOG_COLUMNS,
    STATUS_LOG_FILENAME,
)


class Step(StrEnum):
    """Experiment steps."""

    GET_DATA = "get-data"


class Status(StrEnum):
    """Step statuses."""

    START = "start"
    END = "end"


def _load_status_log(fpath: Path, now: datetime) -> pd.DataFrame:
    """Load the status log, or return an empty one if it does not exist.

    If the file cannot be parsed or is missing expected columns, it is moved to a
    timestamped backup and an empty log is returned.
    """
    if not fpath.exists():
        return pd.DataFrame(columns=STATUS_LOG_COLUMNS)

    try:
        df = pd.read_csv(fpath, sep="\t", dtype=str, keep_default_na=False)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        df = None

    if df is not None and set(STATUS_LOG_COLUMNS).issubset(df.columns):
        return df

    fpath_backup = fpath.with_name(
        f"{fpath.stem}-{now.strftime(BACKUP_TIMESTAMP_FORMAT)}{fpath.suffix}"
    )
    fpath.rename(fpath_backup)
    warnings.warn(f"invalid status log moved to {fpath_backup}", stacklevel=3)
    return pd.DataFrame(columns=STATUS_LOG_COLUMNS)


def record(root: Path, step: Step, status: Status, notes: str = "") -> None:
    """Add a timestamped row to the status log, creating it if needed.

    Warns if a step is started twice or ended without being started.
    """
    now = datetime.now().astimezone()
    df = _load_status_log(fpath := root / BRAINFLEX_DIRNAME / STATUS_LOG_FILENAME, now)

    statuses = df.query(f"{COL_STEP} == @step")[COL_STATUS]
    last_status = statuses.iloc[-1] if not statuses.empty else None
    if status == Status.START and last_status == Status.START:
        warnings.warn(f"step {step} was already started", stacklevel=2)
    elif status == Status.END and last_status != Status.START:
        warnings.warn(f"step {step} was not started", stacklevel=2)

    row = {
        COL_TIMESTAMP: now.isoformat(timespec="seconds"),
        COL_STEP: str(step),
        COL_STATUS: str(status),
        COL_NOTES: notes,
    }
    df = pd.concat([df, pd.DataFrame([row], columns=STATUS_LOG_COLUMNS)])
    df.to_csv(fpath, sep="\t", index=False)
