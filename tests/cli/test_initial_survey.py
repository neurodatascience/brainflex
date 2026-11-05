from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from brainflex.cli.main import app
from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    FAMILIARITY_LABELS,
    INITIAL_SURVEY_FILENAME,
    INITIAL_SURVEY_QUESTIONS,
)


@pytest.fixture
def mock_initial_survey(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("brainflex.cli.initial_survey.initial_survey")


def _answers(*ratings: int) -> dict[str, int]:
    return dict(zip(INITIAL_SURVEY_QUESTIONS, ratings, strict=True))


@pytest.fixture
def fpath_survey(dpath_root: Path) -> Path:
    return dpath_root / BRAINFLEX_DIRNAME / INITIAL_SURVEY_FILENAME


class TestInitialSurvey:
    def test_initial_survey(
        self, runner: CliRunner, mock_initial_survey: MagicMock, dpath_root: Path
    ):
        result = runner.invoke(
            app,
            ["initial-survey", "--project", str(dpath_root)],
            input="1\n3\n5\n",
        )
        assert result.exit_code == 0
        for tool in ("Nipoppy", "Neurobagel", "Fed-BioMed"):
            assert f"How familiar are you with {tool}?" in result.stdout
        # legend is printed once, before the questions
        for i, label in enumerate(FAMILIARITY_LABELS, start=1):
            assert result.stdout.count(f"{i} = {label}") == 1
            assert result.stdout.index(label) < result.stdout.index("How familiar")
        assert "Saved answers to" in result.stdout
        mock_initial_survey.assert_called_once_with(
            dpath_root.resolve(), _answers(1, 3, 5), overwrite=False
        )

    def test_invalid_input_reprompts(
        self, runner: CliRunner, mock_initial_survey: MagicMock, dpath_root: Path
    ):
        result = runner.invoke(
            app,
            ["initial-survey", "--project", str(dpath_root)],
            input="0\nabc\n2\n3\n4\n",
        )
        assert result.exit_code == 0
        mock_initial_survey.assert_called_once_with(
            dpath_root.resolve(), _answers(2, 3, 4), overwrite=False
        )

    def test_default_path(
        self,
        runner: CliRunner,
        mock_initial_survey: MagicMock,
        dpath_subdir: Path,
        dpath_root: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(dpath_subdir)
        result = runner.invoke(app, ["initial-survey"], input="1\n1\n1\n")
        assert result.exit_code == 0
        mock_initial_survey.assert_called_once_with(
            dpath_root.resolve(), _answers(1, 1, 1), overwrite=False
        )

    def test_exists(
        self,
        runner: CliRunner,
        mock_initial_survey: MagicMock,
        dpath_root: Path,
        fpath_survey: Path,
    ):
        fpath_survey.write_text("existing")
        result = runner.invoke(app, ["initial-survey", "--project", str(dpath_root)])
        assert result.exit_code == 1
        assert "How familiar" not in result.stdout
        assert "ERROR" in result.stderr
        assert INITIAL_SURVEY_FILENAME in result.stderr
        mock_initial_survey.assert_not_called()

    def test_exists_overwrite(
        self,
        runner: CliRunner,
        mock_initial_survey: MagicMock,
        dpath_root: Path,
        fpath_survey: Path,
    ):
        fpath_survey.write_text("existing")
        result = runner.invoke(
            app,
            ["initial-survey", "--overwrite", "--project", str(dpath_root)],
            input="1\n1\n1\n",
        )
        assert result.exit_code == 0
        mock_initial_survey.assert_called_once_with(
            dpath_root.resolve(), _answers(1, 1, 1), overwrite=True
        )

    def test_end_to_end(self, runner: CliRunner, dpath_root: Path, fpath_survey: Path):
        result = runner.invoke(
            app,
            ["initial-survey", "--project", str(dpath_root)],
            input="1\n3\n5\n",
        )
        assert result.exit_code == 0
        assert fpath_survey.read_text().splitlines() == [
            "question\tanswer",
            "How familiar are you with Nipoppy?\t1 (I have never heard of it before this project)",
            "How familiar are you with Neurobagel?\t3 (I have used but only with example/toy data)",
            "How familiar are you with Fed-BioMed?\t5 (I use it regularly / It is one of my go-to tools)",
        ]
