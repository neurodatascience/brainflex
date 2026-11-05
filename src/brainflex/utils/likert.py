"""Likert scale utilities."""

from collections.abc import Sequence

from brainflex.utils.constants import LIKERT_CHOICES


def label_likert_answer(answer: str | int, labels: Sequence[str]) -> str:
    """Return a Likert scale answer with its label.

    Raises ValueError if the answer is not a valid choice or if there is not
    exactly one label per choice.
    """
    if len(labels) != len(LIKERT_CHOICES):
        raise ValueError(
            f"Expected {len(LIKERT_CHOICES)} labels, got {len(labels)}: {labels}"
        )
    answer = str(answer)
    if answer not in LIKERT_CHOICES:
        raise ValueError(
            f"Invalid answer {answer!r}: must be one of {', '.join(LIKERT_CHOICES)}"
        )
    return f"{answer} ({labels[LIKERT_CHOICES.index(answer)]})"
