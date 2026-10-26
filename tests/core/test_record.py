from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from brainflex.core.init import init
from brainflex.core.record import Status, Step, record
from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    STATUS_LOG_COLUMNS,
    STATUS_LOG_FILENAME,
)


@pytest.fixture
def root(tmp_path: Path) -> Path:
    init(tmp_path)
    return tmp_path


@pytest.fixture
def fpath_log(root: Path) -> Path:
    return root / BRAINFLEX_DIRNAME / STATUS_LOG_FILENAME


def _read(fpath: Path) -> pd.DataFrame:
    return pd.read_csv(fpath, sep="\t", dtype=str, keep_default_na=False)


class TestRecord:
    def test_creates_file(self, root: Path, fpath_log: Path):
        record(root, Step.GET_DATA, Status.START)
        df = _read(fpath_log)
        assert tuple(df.columns) == STATUS_LOG_COLUMNS
        assert len(df) == 1
        row = df.iloc[0]
        assert row["step"] == "get-data"
        assert row["status"] == "start"
        assert row["notes"] == ""
        assert datetime.fromisoformat(row["timestamp"]).tzinfo is not None

    def test_appends(self, root: Path, fpath_log: Path):
        record(root, Step.GET_DATA, Status.START)
        record(root, Step.GET_DATA, Status.END, notes="went fine")
        df = _read(fpath_log)
        assert list(df["status"]) == ["start", "end"]
        assert list(df["notes"]) == ["", "went fine"]
        assert fpath_log.read_text().count("timestamp") == 1

    def test_notes_with_special_characters(self, root: Path, fpath_log: Path):
        notes = 'tab\there\nnew line and "quotes"'
        record(root, Step.GET_DATA, Status.START)
        record(root, Step.GET_DATA, Status.END, notes=notes)
        assert _read(fpath_log).iloc[-1]["notes"] == notes

    def test_no_warning(self, root: Path, capsys: pytest.CaptureFixture[str]):
        record(root, Step.GET_DATA, Status.START)
        record(root, Step.GET_DATA, Status.END)
        assert "Warning" not in capsys.readouterr().err

    @pytest.mark.parametrize(
        ("statuses", "message"),
        [
            ([Status.END], "was not started"),
            ([Status.START, Status.START], "was already started"),
            ([Status.START, Status.END, Status.END], "was not started"),
        ],
    )
    def test_warning(
        self,
        root: Path,
        fpath_log: Path,
        capsys: pytest.CaptureFixture[str],
        statuses: list[Status],
        message: str,
    ):
        for status in statuses:
            record(root, Step.GET_DATA, status)
        assert message in capsys.readouterr().err
        assert len(_read(fpath_log)) == len(statuses)

    def test_extra_columns_kept(self, root: Path, fpath_log: Path):
        fpath_log.write_text(
            "timestamp\tstep\tstatus\tnotes\textra\nt0\tget-data\tstart\t\tx\n"
        )
        record(root, Step.GET_DATA, Status.END)
        df = _read(fpath_log)
        assert list(df["status"]) == ["start", "end"]
        assert list(df["extra"]) == ["x", ""]

    @pytest.mark.parametrize(
        "content",
        [
            "",
            "timestamp\tstep\tstatus\nt0\tget-data\tstart\n",
            'timestamp\tstep\tstatus\tnotes\n"unclosed\n',
        ],
    )
    def test_invalid_log(
        self,
        root: Path,
        fpath_log: Path,
        capsys: pytest.CaptureFixture[str],
        content: str,
    ):
        fpath_log.write_text(content)
        record(root, Step.GET_DATA, Status.START)

        fpaths_backup = list(fpath_log.parent.glob("status_log-*.tsv"))
        assert len(fpaths_backup) == 1
        assert fpaths_backup[0].read_text() == content
        df = _read(fpath_log)
        assert tuple(df.columns) == STATUS_LOG_COLUMNS
        assert len(df) == 1
        err = capsys.readouterr().err
        assert "invalid status log" in err
        # previous records are discarded, so no start/end warning
        assert "was already started" not in err

    def test_not_initialized(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="not initialized"):
            record(tmp_path, Step.GET_DATA, Status.START)
