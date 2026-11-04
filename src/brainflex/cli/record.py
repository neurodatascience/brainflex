"""CLI for ``brainflex record``."""

from pathlib import Path
from typing import Annotated

import typer
from rich.prompt import Prompt

from brainflex.cli.console import format_scale
from brainflex.cli.options import RootOption
from brainflex.core.record import (
    SCALE_LABELS,
    Status,
    Step,
    get_step_questions,
    record,
)


def record_cli(
    step: Annotated[Step, typer.Argument(help="Experiment step.")],
    status: Annotated[Status, typer.Argument(help="Step status.")],
    path: RootOption = Path(),
) -> None:
    """Record the start or end of an experiment step."""
    answers = {}
    if status == Status.END:
        for question, choices in get_step_questions(step).items():
            if choices is None:
                answers[question] = Prompt.ask(
                    f"{question} (press Enter to leave blank)",
                    default="",
                    show_default=False,
                )
            else:
                if question in SCALE_LABELS:
                    typer.echo(format_scale(SCALE_LABELS[question]))
                answers[question] = Prompt.ask(question, choices=list(choices))
    fpath_timestamps, fpath_survey = record(path, step, status, answers=answers)
    typer.echo(f"Saved timestamp for ({step}, {status}) to {fpath_timestamps}")
    if fpath_survey is not None:
        typer.echo(f"Saved answers to {fpath_survey}")
