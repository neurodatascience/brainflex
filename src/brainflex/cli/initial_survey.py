"""CLI for ``brainflex initial-survey``."""

from pathlib import Path
from typing import Annotated

import typer
from rich.prompt import Prompt

from brainflex.cli.console import print_error
from brainflex.cli.options import RootOption
from brainflex.core.initial_survey import check_initial_survey_path, initial_survey
from brainflex.utils.constants import LIKERT_CHOICES

TOOLS = ("Nipoppy", "Neurobagel", "Fed-BioMed")


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

    typer.echo("Rate your familiarity (1 = not at all familiar, 5 = very familiar)")
    nipoppy, neurobagel, fedbiomed = (
        int(Prompt.ask(f"How familiar are you with {tool}?", choices=LIKERT_CHOICES))
        for tool in TOOLS
    )
    initial_survey(path, nipoppy, neurobagel, fedbiomed, overwrite=overwrite)
    typer.echo(f"Saved answers to {fpath}")
