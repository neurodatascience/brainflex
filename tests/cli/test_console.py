import warnings

import pytest

from brainflex.cli.console import format_scale, print_error, render_warnings


class TestFormatScale:
    def test_format_scale(self):
        assert format_scale(["a", "b", "c", "d", "e"]).plain.splitlines() == [
            "  1 = a",
            "  2 = b",
            "  3 = c",
            "  4 = d",
            "  5 = e",
        ]

    def test_choices_styled_like_prompt(self):
        text = format_scale(["a", "b", "c", "d", "e"])
        styled = [
            text.plain[span.start : span.end]
            for span in text.spans
            if span.style == "prompt.choices"
        ]
        assert styled == ["1", "2", "3", "4", "5"]

    @pytest.mark.parametrize("labels", [["a", "b", "c", "d"], list("abcdef")])
    def test_wrong_number_of_labels(self, labels: list[str]):
        with pytest.raises(ValueError, match="zip"):
            format_scale(labels)


class TestPrintError:
    def test_print_error(self, capsys: pytest.CaptureFixture[str]):
        print_error(FileNotFoundError("missing: ['sub-01']"))
        assert capsys.readouterr().err == "ERROR: missing: ['sub-01']\n"


class TestRenderWarnings:
    def test_render_warnings(self, capsys: pytest.CaptureFixture[str]):
        with render_warnings():
            warnings.warn("missing: ['sub-01']", stacklevel=1)
        assert capsys.readouterr().err == "WARNING: missing: ['sub-01']\n"

    def test_repeated(self, capsys: pytest.CaptureFixture[str]):
        with render_warnings():
            for _ in range(2):
                warnings.warn("repeated", stacklevel=1)
        assert capsys.readouterr().err == "WARNING: repeated\n" * 2

    def test_restores_showwarning(self):
        showwarning = warnings.showwarning
        with render_warnings():
            pass
        assert warnings.showwarning is showwarning
