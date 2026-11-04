from pathlib import Path

import pandas as pd
import pytest

from brainflex.core.initial_survey import check_initial_survey_path, initial_survey
from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    INITIAL_SURVEY_FILENAME,
    INITIAL_SURVEY_QUESTIONS,
    SURVEY_COLUMNS,
)


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / BRAINFLEX_DIRNAME).mkdir()
    return tmp_path


@pytest.fixture
def fpath_survey(root: Path) -> Path:
    return root / BRAINFLEX_DIRNAME / INITIAL_SURVEY_FILENAME


def _read(fpath: Path) -> pd.DataFrame:
    return pd.read_csv(fpath, sep="\t", dtype=str, keep_default_na=False)


def _answers(*ratings: int) -> dict[str, int]:
    return dict(zip(INITIAL_SURVEY_QUESTIONS, ratings, strict=True))


class TestCheckInitialSurveyPath:
    def test_not_exists(self, root: Path, fpath_survey: Path):
        assert check_initial_survey_path(root) == fpath_survey

    def test_exists(self, root: Path, fpath_survey: Path):
        fpath_survey.write_text("existing")
        with pytest.raises(FileExistsError, match=str(fpath_survey)):
            check_initial_survey_path(root)

    def test_exists_overwrite(self, root: Path, fpath_survey: Path):
        fpath_survey.write_text("existing")
        assert check_initial_survey_path(root, overwrite=True) == fpath_survey


class TestInitialSurvey:
    def test_creates_file(self, root: Path, fpath_survey: Path):
        initial_survey(root, _answers(1, 3, 5))
        df = _read(fpath_survey)
        assert tuple(df.columns) == SURVEY_COLUMNS
        assert list(df["question"]) == [
            "How familiar are you with Nipoppy?",
            "How familiar are you with Neurobagel?",
            "How familiar are you with Fed-BioMed?",
        ]
        assert list(df["answer"]) == [
            "1 (I have never heard of it before this project)",
            "3 (I have used but only with example/toy data)",
            "5 (I use it regularly / It is one of my go-to tools)",
        ]

    def test_question_order(self, root: Path, fpath_survey: Path):
        answers = dict(reversed(_answers(1, 3, 5).items()))
        initial_survey(root, answers)
        df = _read(fpath_survey)
        assert list(df["question"]) == list(INITIAL_SURVEY_QUESTIONS)
        assert list(df["answer"]) == [
            "1 (I have never heard of it before this project)",
            "3 (I have used but only with example/toy data)",
            "5 (I use it regularly / It is one of my go-to tools)",
        ]

    def test_exists(self, root: Path, fpath_survey: Path):
        fpath_survey.write_text("existing")
        with pytest.raises(FileExistsError, match="--overwrite"):
            initial_survey(root, _answers(1, 1, 1))
        assert fpath_survey.read_text() == "existing"

    def test_overwrite(self, root: Path, fpath_survey: Path):
        initial_survey(root, _answers(1, 1, 1))
        initial_survey(root, _answers(2, 2, 2), overwrite=True)
        df = _read(fpath_survey)
        assert len(df) == len(INITIAL_SURVEY_QUESTIONS)
        assert list(df["answer"]) == ["2 (I have heard of it but never used)"] * 3

    @pytest.mark.parametrize("ratings", [(0, 1, 1), (1, 6, 1), (1, 1, -1)])
    def test_invalid_rating(
        self, root: Path, fpath_survey: Path, ratings: tuple[int, int, int]
    ):
        with pytest.raises(ValueError, match="must be one of"):
            initial_survey(root, _answers(*ratings))
        assert not fpath_survey.exists()

    @pytest.mark.parametrize(
        "answers",
        [
            dict(list(_answers(1, 1, 1).items())[:2]),
            {**_answers(1, 1, 1), "Unknown question?": 1},
        ],
    )
    def test_invalid_questions(
        self, root: Path, fpath_survey: Path, answers: dict[str, int]
    ):
        with pytest.raises(ValueError, match="exactly these questions"):
            initial_survey(root, answers)
        assert not fpath_survey.exists()
