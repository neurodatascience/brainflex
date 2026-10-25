from pathlib import Path

import pytest

from brainflex.core.init import init
from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    DATA_DIRNAME,
    STATUS_LOG_FILENAME,
)


class TestInit:
    def test_init(self, tmp_path: Path):
        init(tmp_path)
        assert (tmp_path / DATA_DIRNAME).is_dir()
        assert (tmp_path / BRAINFLEX_DIRNAME).is_dir()
        assert not (tmp_path / BRAINFLEX_DIRNAME / STATUS_LOG_FILENAME).exists()

    def test_init_creates_root(self, tmp_path: Path):
        root = tmp_path / "new_project"
        init(root)
        assert (root / BRAINFLEX_DIRNAME).is_dir()

    def test_init_existing_data_dir(self, tmp_path: Path):
        (tmp_path / DATA_DIRNAME).mkdir()
        (tmp_path / DATA_DIRNAME / "file.txt").write_text("keep me")
        init(tmp_path)
        assert (tmp_path / DATA_DIRNAME / "file.txt").read_text() == "keep me"

    def test_init_already_initialized(self, tmp_path: Path):
        init(tmp_path)
        fpath = tmp_path / BRAINFLEX_DIRNAME / "file.txt"
        fpath.write_text("keep me")

        with pytest.raises(FileExistsError, match="already initialized"):
            init(tmp_path)
        assert fpath.read_text() == "keep me"
