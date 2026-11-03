from pathlib import Path

import pandas as pd
import pytest

from brainflex.utils.tsv import append_tsv, load_tsv

COLUMNS = ("a", "b")


@pytest.fixture
def fpath(tmp_path: Path) -> Path:
    return tmp_path / "file.tsv"


def _read(fpath: Path) -> pd.DataFrame:
    return pd.read_csv(fpath, sep="\t", dtype=str, keep_default_na=False)


class TestLoadTsv:
    def test_missing(self, fpath: Path):
        df = load_tsv(fpath, COLUMNS)
        assert tuple(df.columns) == COLUMNS
        assert df.empty
        assert not fpath.exists()

    def test_valid(self, fpath: Path):
        fpath.write_text("a\tb\textra\n1\t2\tx\n")
        df = load_tsv(fpath, COLUMNS)
        assert df.to_dict("records") == [{"a": "1", "b": "2", "extra": "x"}]

    @pytest.mark.parametrize("content", ["", "a\n1\n", 'a\tb\n"unclosed\n'])
    def test_invalid(self, fpath: Path, content: str):
        fpath.write_text(content)
        with pytest.warns(UserWarning, match="invalid file"):
            df = load_tsv(fpath, COLUMNS)
        assert tuple(df.columns) == COLUMNS
        assert df.empty
        assert not fpath.exists()
        fpaths_backup = list(fpath.parent.glob("file-*.tsv"))
        assert len(fpaths_backup) == 1
        assert fpaths_backup[0].read_text() == content


class TestAppendTsv:
    def test_creates_file(self, fpath: Path):
        append_tsv(fpath, COLUMNS, [{"a": "1", "b": "2"}])
        assert fpath.read_text() == "a\tb\n1\t2\n"

    def test_appends(self, fpath: Path):
        append_tsv(fpath, COLUMNS, [{"a": "1", "b": "2"}])
        append_tsv(fpath, COLUMNS, ({"a": str(i), "b": ""} for i in range(2)))
        assert list(_read(fpath)["a"]) == ["1", "0", "1"]

    def test_extra_columns_kept(self, fpath: Path):
        fpath.write_text("a\tb\textra\n1\t2\tx\n")
        append_tsv(fpath, COLUMNS, [{"a": "3", "b": "4"}])
        assert list(_read(fpath)["extra"]) == ["x", ""]

    def test_special_characters(self, fpath: Path):
        value = 'tab\there\nnew line and "quotes"'
        append_tsv(fpath, COLUMNS, [{"a": value, "b": ""}])
        assert _read(fpath).iloc[0]["a"] == value

    def test_given_df(self, fpath: Path):
        df = pd.DataFrame([{"a": "0", "b": "0"}], columns=COLUMNS)
        append_tsv(fpath, COLUMNS, [{"a": "1", "b": "2"}], df=df)
        assert list(_read(fpath)["a"]) == ["0", "1"]
