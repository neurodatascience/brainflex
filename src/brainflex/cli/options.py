"""Options shared across CLI commands."""

from pathlib import Path
from typing import Annotated

import typer

from brainflex.utils.paths import find_root

RootOption = Annotated[
    Path,
    typer.Option(
        "--path",
        file_okay=False,
        resolve_path=True,
        callback=find_root,
        help="Project root directory, or any subdirectory of it.",
    ),
]
