"""CLI for ``brainflex init``."""

from pathlib import Path
from typing import Annotated

import typer

from brainflex.cli.console import print_error
from brainflex.cli.options import RootOption
from brainflex.core.init import init
from brainflex.utils.constants import (
    ENV_FILENAME,
    VPN_CONFIG_DIRNAME,
    VPN_CONFIG_FILENAME,
)


def init_cli(
    vpn_config: Annotated[
        Path,
        typer.Argument(
            dir_okay=False,
            resolve_path=True,
            help="VPN configuration file received from the project coordinator.",
        ),
    ],
    path: RootOption = Path(),
) -> None:
    """Create the Docker Compose configuration (.env and VPN configuration files)."""
    try:
        init(path, vpn_config)
    except (FileExistsError, FileNotFoundError) as e:
        print_error(e)
        raise typer.Exit(1) from e
    typer.echo(f"Created {path / ENV_FILENAME}")
    typer.echo(f"Created {path / VPN_CONFIG_DIRNAME / VPN_CONFIG_FILENAME}")
