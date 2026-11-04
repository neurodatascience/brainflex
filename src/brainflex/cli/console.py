"""Console output shared across CLI commands."""

import warnings
from collections.abc import Iterator, Sequence
from contextlib import contextmanager

from rich.console import Console
from rich.markup import escape
from rich.text import Text

from brainflex.utils.constants import LIKERT_CHOICES

console = Console(stderr=True)


def print_error(message: object) -> None:
    """Print an error message to stderr."""
    console.print(f"[red]ERROR:[/red] {escape(str(message))}", soft_wrap=True)


def format_scale(labels: Sequence[str]) -> Text:
    """Format a Likert scale legend with one line per choice.

    Raises ValueError if there is not exactly one label per choice.
    """
    return Text("\n").join(
        Text.assemble("  ", (choice, "prompt.choices"), f" = {label}")
        for choice, label in zip(LIKERT_CHOICES, labels, strict=True)
    )


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
