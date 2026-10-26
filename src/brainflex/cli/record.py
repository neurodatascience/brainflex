"""CLI for ``brainflex record``."""

from pathlib import Path
from typing import Annotated

import typer
from rich.prompt import Prompt

from brainflex.core.record import Status, Step, record


def record_cli(
    step: Annotated[Step, typer.Argument(help="Experiment step.")],
    status: Annotated[Status, typer.Argument(help="Step status.")],
    path: Annotated[
        Path,
        typer.Argument(
            file_okay=False,
            resolve_path=True,
            help="Project root directory.",
        ),
    ] = Path(),
) -> None:
    """Record the start or end of an experiment step."""
    notes = ""
    if status == Status.END:
        notes = Prompt.ask(
            "Notes/feedback (press Enter to leave blank)",
            default=notes,
            show_default=False,
        )
    try:
        record(path, step, status, notes=notes)
    except FileNotFoundError as e:
        typer.echo(f"{e}. Run brainflex init.", err=True)
        raise typer.Exit(1) from e
    typer.echo(f"Recorded {step} {status}")
