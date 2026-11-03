from pathlib import Path

import pandas as pd
import pytest

from brainflex.core.initial_survey import check_initial_survey_path, initial_survey
from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    INITIAL_SURVEY_COLUMNS,
    INITIAL_SURVEY_FILENAME,
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
        initial_survey(root, 1, 3, 5)
        df = _read(fpath_survey)
        assert tuple(df.columns) == INITIAL_SURVEY_COLUMNS
        assert len(df) == 1
        row = df.iloc[0]
        assert row["nipoppy_familiarity"] == "1"
        assert row["neurobagel_familiarity"] == "3"
        assert row["fedbiomed_familiarity"] == "5"

    def test_exists(self, root: Path, fpath_survey: Path):
        fpath_survey.write_text("existing")
        with pytest.raises(FileExistsError, match="--overwrite"):
            initial_survey(root, 1, 1, 1)
        assert fpath_survey.read_text() == "existing"

    def test_overwrite(self, root: Path, fpath_survey: Path):
        initial_survey(root, 1, 1, 1)
        initial_survey(root, 2, 2, 2, overwrite=True)
        df = _read(fpath_survey)
        assert len(df) == 1
        assert df.iloc[0]["nipoppy_familiarity"] == "2"

    @pytest.mark.parametrize("ratings", [(0, 1, 1), (1, 6, 1), (1, 1, -1)])
    def test_invalid_rating(
        self, root: Path, fpath_survey: Path, ratings: tuple[int, int, int]
    ):
        with pytest.raises(ValueError, match="must be one of"):
            initial_survey(root, *ratings)
        assert not fpath_survey.exists()
