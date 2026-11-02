"""Console output shared across CLI commands."""

import warnings
from collections.abc import Iterator
from contextlib import contextmanager

from rich.console import Console
from rich.markup import escape

console = Console(stderr=True)


def print_error(message: object) -> None:
    """Print an error message to stderr."""
    console.print(f"[red]ERROR:[/red] {escape(str(message))}", soft_wrap=True)


def _show_warning(message: Warning | str, *args: object, **kwargs: object) -> None:
    """Print a warning message to stderr."""
    console.print(f"[yellow]WARNING:[/yellow] {escape(str(message))}", soft_wrap=True)


@contextmanager
def render_warnings() -> Iterator[None]:
    """Print all warnings raised in this context with the console."""
    with warnings.catch_warnings():
        warnings.simplefilter("always")
        warnings.showwarning = _show_warning
        yield
