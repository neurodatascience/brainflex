"""TSV file utilities."""

import warnings
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime
from pathlib import Path

import pandas as pd

from brainflex.utils.constants import BACKUP_TIMESTAMP_FORMAT


def load_tsv(fpath: Path, columns: Sequence[str]) -> pd.DataFrame:
    """Load a TSV file, or return an empty one if it does not exist.

    If the file cannot be parsed or is missing expected columns, it is moved to a
    timestamped backup and an empty dataframe is returned.
    """
    if not fpath.exists():
        return pd.DataFrame(columns=columns)

    try:
        df = pd.read_csv(fpath, sep="\t", dtype=str, keep_default_na=False)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        df = None

    if df is not None and set(columns).issubset(df.columns):
        return df

    now = datetime.now().astimezone()
    fpath_backup = fpath.with_name(
        f"{fpath.stem}-{now.strftime(BACKUP_TIMESTAMP_FORMAT)}{fpath.suffix}"
    )
    fpath.rename(fpath_backup)
    warnings.warn(f"invalid file {fpath} moved to {fpath_backup}", stacklevel=3)
    return pd.DataFrame(columns=columns)


def append_tsv(
    fpath: Path,
    columns: Sequence[str],
    rows: Iterable[Mapping[str, str]],
    df: pd.DataFrame | None = None,
) -> None:
    """Append rows to a TSV file, creating it if needed."""
    if df is None:
        df = load_tsv(fpath, columns)
    df = pd.concat([df, pd.DataFrame(list(rows), columns=columns)])
    df.to_csv(fpath, sep="\t", index=False)
