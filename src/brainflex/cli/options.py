"""Options shared across CLI commands."""

from pathlib import Path
from typing import Annotated

import typer

from brainflex.utils.paths import find_root


def _root_callback(path: Path) -> Path:
    try:
        return find_root(path)
    except FileNotFoundError as e:
        raise typer.BadParameter(str(e)) from e


RootOption = Annotated[
    Path,
    typer.Option(
        "--project",
        file_okay=False,
        resolve_path=True,
        callback=_root_callback,
        help="Project root directory, or any subdirectory of it.",
    ),
]
