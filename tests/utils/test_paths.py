from pathlib import Path

from brainflex.utils.constants import BRAINFLEX_DIRNAME
from brainflex.utils.paths import find_root


class TestFindRoot:
    def test_root(self, tmp_path: Path):
        (tmp_path / BRAINFLEX_DIRNAME).mkdir()
        assert find_root(tmp_path) == tmp_path

    def test_subdirectory(self, tmp_path: Path):
        (tmp_path / BRAINFLEX_DIRNAME).mkdir()
        dpath = tmp_path / "data" / "ds000001"
        dpath.mkdir(parents=True)
        assert find_root(dpath) == tmp_path

    def test_not_found(self, tmp_path: Path):
        dpath = tmp_path / "data"
        dpath.mkdir()
        assert find_root(dpath) == dpath

    def test_nested(self, tmp_path: Path):
        (tmp_path / BRAINFLEX_DIRNAME).mkdir()
        dpath_inner = tmp_path / "inner"
        (dpath_inner / BRAINFLEX_DIRNAME).mkdir(parents=True)
        dpath = dpath_inner / "data"
        dpath.mkdir()
        assert find_root(dpath) == dpath_inner

    def test_file_ignored(self, tmp_path: Path):
        (tmp_path / BRAINFLEX_DIRNAME).touch()
        dpath = tmp_path / "data"
        dpath.mkdir()
        assert find_root(dpath) == dpath
