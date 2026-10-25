"""Main CLI entry point."""

from typing import Annotated

import typer

from brainflex import __version__
from brainflex.cli.check import check_cli
from brainflex.cli.get_data import get_data_cli
from brainflex.cli.init import init_cli

app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
) -> None:
    """Brain federated learning experiment."""


app.command("check")(check_cli)
app.command("get-data")(get_data_cli)
app.command("init")(init_cli)
