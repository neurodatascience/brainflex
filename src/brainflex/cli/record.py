"""CLI for ``brainflex record``."""

from pathlib import Path
from typing import Annotated

import typer
from rich.prompt import Prompt

from brainflex.cli.options import RootOption
from brainflex.core.record import Status, Step, record


def record_cli(
    step: Annotated[Step, typer.Argument(help="Experiment step.")],
    status: Annotated[Status, typer.Argument(help="Step status.")],
    path: RootOption = Path(),
) -> None:
    """Record the start or end of an experiment step."""
    notes = ""
    if status == Status.END:
        notes = Prompt.ask(
            "Notes/feedback (press Enter to leave blank)",
            default=notes,
            show_default=False,
        )
    record(path, step, status, notes=notes)
    typer.echo(f"Recorded {step} {status}")
