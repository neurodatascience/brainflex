"""Record the start and end of experiment steps."""

from datetime import datetime
from enum import StrEnum
from pathlib import Path

import pandas as pd
from rich.console import Console

from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    COL_NOTES,
    COL_STATUS,
    COL_STEP,
    COL_TIMESTAMP,
    STATUS_LOG_COLUMNS,
    STATUS_LOG_FILENAME,
)

console = Console(stderr=True)


class Step(StrEnum):
    """Experiment steps."""

    GET_DATA = "get-data"


class Status(StrEnum):
    """Step statuses."""

    START = "start"
    END = "end"


def record(root: Path, step: Step, status: Status, notes: str = "") -> None:
    """Add a timestamped row to the status log, creating it if needed.

    Warns if a step is started twice or ended without being started.
    Raises FileNotFoundError if the project is not initialized.
    """
    dpath_brainflex = root / BRAINFLEX_DIRNAME
    if not dpath_brainflex.is_dir():
        raise FileNotFoundError(
            f"Project not initialized: {dpath_brainflex} not found"
        )

    fpath = dpath_brainflex / STATUS_LOG_FILENAME
    if fpath.exists():
        df = pd.read_csv(fpath, sep="\t", dtype=str, keep_default_na=False)
    else:
        df = pd.DataFrame(columns=STATUS_LOG_COLUMNS)

    statuses = df.loc[df[COL_STEP] == step, COL_STATUS]
    last_status = statuses.iloc[-1] if not statuses.empty else None
    if status == Status.START and last_status == Status.START:
        console.print(
            f"[yellow]Warning:[/yellow] step {step} was already started", soft_wrap=True
        )
    elif status == Status.END and last_status != Status.START:
        console.print(
            f"[yellow]Warning:[/yellow] step {step} was not started", soft_wrap=True
        )

    row = {
        COL_TIMESTAMP: datetime.now().astimezone().isoformat(timespec="seconds"),
        COL_STEP: str(step),
        COL_STATUS: str(status),
        COL_NOTES: notes,
    }
    df = pd.concat([df, pd.DataFrame([row], columns=STATUS_LOG_COLUMNS)])
    df.to_csv(fpath, sep="\t", index=False)
