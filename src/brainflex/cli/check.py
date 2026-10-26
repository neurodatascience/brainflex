"""CLI for ``brainflex check``."""

from pathlib import Path
from typing import Annotated

import typer

from brainflex.core.check import check
from brainflex.utils.paths import find_root


def check_cli(
    path: Annotated[
        Path,
        typer.Argument(
            file_okay=False,
            resolve_path=True,
            callback=find_root,
            help="Project root directory, or any subdirectory of it.",
        ),
    ] = Path(),
) -> None:
    """Check that prerequisites are satisfied."""
    failed = False
    for result in check(path):
        if result.passed:
            label = typer.style("OK", fg=typer.colors.GREEN)
        elif result.required:
            label = typer.style("FAIL", fg=typer.colors.RED)
            failed = True
        else:
            label = typer.style("WARN", fg=typer.colors.YELLOW)
        typer.echo(f"[{label}] {result.name}: {result.message}")
    if failed:
        raise typer.Exit(1)
