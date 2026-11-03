"""CLI for ``brainflex record``."""

from pathlib import Path
from typing import Annotated

import typer
from rich.prompt import Prompt

from brainflex.cli.options import RootOption
from brainflex.core.record import Status, Step, get_step_questions, record
from brainflex.utils.constants import QUESTION_TOOLS_EASIER

HINTS = {QUESTION_TOOLS_EASIER: "1 = not at all, 5 = a lot"}


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
                hint = f" ({HINTS[question]})" if question in HINTS else ""
                answers[question] = Prompt.ask(
                    f"{question}{hint}", choices=list(choices)
                )
    fpath_timestamps, fpath_survey = record(path, step, status, answers=answers)
    typer.echo(f"Saved timestamp for ({step}, {status}) to {fpath_timestamps}")
    if fpath_survey is not None:
        typer.echo(f"Saved answers to {fpath_survey}")
