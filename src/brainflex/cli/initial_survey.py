"""CLI for ``brainflex initial-survey``."""

from pathlib import Path
from typing import Annotated

import typer
from rich import get_console
from rich.prompt import Prompt

from brainflex.cli.console import format_scale, print_error
from brainflex.cli.options import RootOption
from brainflex.core.initial_survey import check_initial_survey_path, initial_survey
from brainflex.utils.constants import (
    FAMILIARITY_LABELS,
    INITIAL_SURVEY_QUESTIONS,
    LIKERT_CHOICES,
)


def initial_survey_cli(
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Replace existing survey answers."),
    ] = False,
    path: RootOption = Path(),
) -> None:
    """Answer a survey on prior experience with the tools used in the experiment."""
    # check before asking questions so that answers are not lost
    try:
        fpath = check_initial_survey_path(path, overwrite=overwrite)
    except FileExistsError as e:
        print_error(e)
        raise typer.Exit(1) from e

    typer.echo("Rate your familiarity with each tool:")
    # same console as Prompt
    get_console().print(format_scale(FAMILIARITY_LABELS), soft_wrap=True)
    answers = {
        question: int(Prompt.ask(question, choices=LIKERT_CHOICES))
        for question in INITIAL_SURVEY_QUESTIONS
    }
    initial_survey(path, answers, overwrite=overwrite)
    typer.echo(f"Saved answers to {fpath}")
