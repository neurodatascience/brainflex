import warnings

import pytest

from brainflex.cli.console import print_error, render_warnings


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
