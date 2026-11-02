import os
from pathlib import Path

import pytest

from brainflex.core.init import _set_variable, init
from brainflex.utils.constants import (
    BRAINFLEX_DIRNAME,
    ENV_EXAMPLE_FILENAME,
    ENV_FILENAME,
    PACKAGE_DATA_DIR,
    VPN_CONFIG_DIRNAME,
    VPN_CONFIG_FILENAME,
)

VPN_CONFIG = "export VPN_IP=10.221.0.2\n"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """Project root with a brainflex directory."""
    (tmp_path / BRAINFLEX_DIRNAME).mkdir()
    return tmp_path


@pytest.fixture
def env_example() -> str:
    """Example .env file shipped with brainflex."""
    return (PACKAGE_DATA_DIR / ENV_EXAMPLE_FILENAME).read_text()


@pytest.fixture
def fpath_vpn_config(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """VPN configuration file received from the VPN server administrator."""
    fpath = tmp_path_factory.mktemp("download") / VPN_CONFIG_FILENAME
    fpath.write_text(VPN_CONFIG)
    return fpath


def _fpath_vpn_config_dst(root: Path) -> Path:
    return root / VPN_CONFIG_DIRNAME / VPN_CONFIG_FILENAME


class TestSetVariable:
    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            ("#VAR=\n", "VAR=1\n"),
            ("# VAR=\n", "VAR=1\n"),
            ("VAR=0\n", "VAR=1\n"),
            ("A=a\n#VAR=\nB=b\n", "A=a\nVAR=1\nB=b\n"),
            ("#\nVAR=0\n", "#\nVAR=1\n"),
            ("#VAR=\n#VAR=\n", "VAR=1\n#VAR=\n"),
            ("A=a\n", "A=a\nVAR=1\n"),
            ("A=a", "A=a\nVAR=1\n"),
            ("", "VAR=1\n"),
            ("#OTHER_VAR=\n", "#OTHER_VAR=\nVAR=1\n"),
        ],
    )
    def test_set_variable(self, content: str, expected: str):
        assert _set_variable(content, "VAR", "1") == expected


class TestInit:
    def test_init(self, root: Path, fpath_vpn_config: Path, env_example: str):
        init(root, fpath_vpn_config)
        content = (root / ENV_FILENAME).read_text()
        # the variables are uncommented, not appended
        assert content == env_example.replace(
            "#CONTAINER_UID=", f"CONTAINER_UID={os.getuid()}"
        ).replace("#CONTAINER_GID=", f"CONTAINER_GID={os.getgid()}").replace(
            "#NIPOPPY_ROOT=", "NIPOPPY_ROOT=./nipoppy_study"
        )
        assert content != env_example

        fpath_dst = _fpath_vpn_config_dst(root)
        assert fpath_dst.read_text() == VPN_CONFIG
        assert fpath_dst.stat().st_mode & 0o777 == 0o600
        assert fpath_vpn_config.read_text() == VPN_CONFIG

    def test_init_vpn_config_already_in_place(self, root: Path):
        fpath_dst = _fpath_vpn_config_dst(root)
        fpath_dst.parent.mkdir()
        fpath_dst.write_text(VPN_CONFIG)
        init(root, fpath_dst)
        assert (root / ENV_FILENAME).exists()
        assert fpath_dst.read_text() == VPN_CONFIG
        assert fpath_dst.stat().st_mode & 0o777 == 0o600

    def test_init_no_vpn_config(self, root: Path, tmp_path_factory):
        fpath = tmp_path_factory.mktemp("download") / VPN_CONFIG_FILENAME
        with pytest.raises(FileNotFoundError, match="VPN configuration file"):
            init(root, fpath)
        assert not (root / ENV_FILENAME).exists()
        assert not _fpath_vpn_config_dst(root).exists()

    def test_init_env_exists(self, root: Path, fpath_vpn_config: Path):
        fpath = root / ENV_FILENAME
        fpath.write_text("keep me")
        with pytest.raises(FileExistsError, match="already initialized"):
            init(root, fpath_vpn_config)
        assert fpath.read_text() == "keep me"
        assert not _fpath_vpn_config_dst(root).exists()

    def test_init_vpn_config_exists(self, root: Path, fpath_vpn_config: Path):
        fpath_dst = _fpath_vpn_config_dst(root)
        fpath_dst.parent.mkdir()
        fpath_dst.write_text("keep me")
        with pytest.raises(FileExistsError, match="already initialized"):
            init(root, fpath_vpn_config)
        assert fpath_dst.read_text() == "keep me"
        assert not (root / ENV_FILENAME).exists()
