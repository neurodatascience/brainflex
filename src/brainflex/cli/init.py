"""CLI for ``brainflex init``."""

from pathlib import Path
from typing import Annotated

import typer

from brainflex.core.init import init


def init_cli(
    path: Annotated[
        Path,
        typer.Argument(
            file_okay=False,
            resolve_path=True,
            help="Project root directory (created if it does not exist).",
        ),
    ] = Path(),
) -> None:
    """Initialize a project directory."""
    try:
        init(path)
    except FileExistsError as e:
        typer.echo(e, err=True)
        raise typer.Exit(1) from e
    typer.echo(f"Initialized project in {path}")
