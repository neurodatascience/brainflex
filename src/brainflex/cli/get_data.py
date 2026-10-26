"""CLI for ``brainflex get-data``."""

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from brainflex.cli.options import RootOption
from brainflex.core.get_data import get_data


def get_data_cli(
    dataset_id: Annotated[
        str,
        typer.Argument(help="OpenNeuro dataset ID, of the form ds######."),
    ],
    path: RootOption = Path(),
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            "--force",
            "-f",
            help="Replace the dataset if it already exists.",
        ),
    ] = False,
    full_rawbids: Annotated[
        bool,
        typer.Option(
            "--full-rawbids",
            help="Download raw BIDS imaging files instead of empty placeholders.",
        ),
    ] = False,
    full_freesurfer: Annotated[
        bool,
        typer.Option(
            "--full-freesurfer",
            help="Download all FreeSurfer outputs instead of stats/ and scripts/ only.",
        ),
    ] = False,
) -> None:
    """Download an OpenNeuro dataset and format it as a Nipoppy study."""
    try:
        dpath_study = get_data(
            path,
            dataset_id,
            overwrite=overwrite,
            full_rawbids=full_rawbids,
            full_freesurfer=full_freesurfer,
        )
    except FileExistsError as e:
        typer.echo(f"{e}. Use --overwrite to replace it.", err=True)
        raise typer.Exit(1) from e
    except (ValueError, subprocess.CalledProcessError) as e:
        typer.echo(e, err=True)
        raise typer.Exit(1) from e
    typer.echo(f"Downloaded {dataset_id} to {dpath_study}")
