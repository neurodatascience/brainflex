"""CLI for ``brainflex record``."""

from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich import get_console
from rich.prompt import Prompt
from rich.text import Text

from brainflex.cli.options import RootOption
from brainflex.core.record import (
    Status,
    Step,
    check_status,
    get_step_questions,
    get_step_summary,
    record,
)


def record_cli(
    step: Annotated[Step, typer.Argument(help="Experiment step.")],
    status: Annotated[Status, typer.Argument(help="Step status.")],
    path: RootOption = Path(),
) -> None:
    """Record the start or end of an experiment step."""
    timestamp = datetime.now().astimezone()

    # warn before asking questions
    check_status(path, step, status)

    answers = {}
    if status == Status.END:
        if (summary := get_step_summary(step)) is not None:
            # same console and colour as Prompt choices
            get_console().print(Text(summary, style="prompt.choices"), end="\n\n")
        for question, choices in get_step_questions(step).items():
            if choices is None:
                answers[question] = Prompt.ask(
                    f"{question} (press Enter to leave blank)",
                    default="",
                    show_default=False,
                )
            else:
                answers[question] = Prompt.ask(question, choices=list(choices))
    fpath_timestamps, fpath_survey = record(
        path, step, status, answers=answers, timestamp=timestamp
    )
    typer.echo(f"Saved timestamp for ({step}, {status}) to {fpath_timestamps}")
    if fpath_survey is not None:
        typer.echo(f"Saved answers to {fpath_survey}")
