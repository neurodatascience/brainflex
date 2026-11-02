"""Project initialization."""

import os
import re
import shutil
from pathlib import Path

from brainflex.utils.constants import (
    ENV_EXAMPLE_FILENAME,
    ENV_FILENAME,
    ENV_VAR_GID,
    ENV_VAR_NIPOPPY_ROOT,
    ENV_VAR_NODE_NAME,
    ENV_VAR_UID,
    NIPOPPY_STUDY_DIRNAME,
    PACKAGE_DATA_DIR,
    VPN_CONFIG_DIRNAME,
    VPN_CONFIG_FILENAME,
    VPN_CONFIG_VAR_NODE_ID,
)


def _set_variable(content: str, name: str, value: str) -> str:
    """Set a variable in .env file content, uncommenting it if needed.

    The variable is appended if it is not in the content.
    """
    line = f"{name}={value}"
    pattern = re.compile(rf"^#?[ \t]*{re.escape(name)}=.*$", flags=re.MULTILINE)
    content, n_subs = pattern.subn(line, content, count=1)
    if n_subs == 0:
        if content and not content.endswith("\n"):
            content += "\n"
        content += f"{line}\n"
    return content


def _get_variable(content: str, name: str) -> str | None:
    """Get the value of a variable in VPN configuration file content.

    Returns None if the variable is not set.
    """
    pattern = re.compile(
        rf"^[ \t]*(?:export[ \t]+)?{re.escape(name)}=(.*)$", flags=re.MULTILINE
    )
    match = pattern.search(content)
    if match is None:
        return None
    return match.group(1).strip().strip("\"'") or None


def init(root: Path, fpath_vpn_config: Path) -> None:
    """Create the Docker Compose configuration of the project.

    Raises FileNotFoundError if the VPN configuration file doesn't exist, and
    FileExistsError if the .env file or the VPN configuration file already exists in
    the project, and ValueError if the VPN configuration file has no node ID.
    """
    if not fpath_vpn_config.is_file():
        raise FileNotFoundError(f"VPN configuration file {fpath_vpn_config} not found")

    fpath_env = root / ENV_FILENAME
    if fpath_env.exists():
        raise FileExistsError(f"Project already initialized: {fpath_env} exists")

    fpath_vpn_config_dst = root / VPN_CONFIG_DIRNAME / VPN_CONFIG_FILENAME
    # the file may already have been put in the right place
    copy_vpn_config = not (
        fpath_vpn_config_dst.exists()
        and fpath_vpn_config.resolve() == fpath_vpn_config_dst.resolve()
    )
    if copy_vpn_config and fpath_vpn_config_dst.exists():
        raise FileExistsError(
            f"Project already initialized: {fpath_vpn_config_dst} exists"
        )

    node_id = _get_variable(fpath_vpn_config.read_text(), VPN_CONFIG_VAR_NODE_ID)
    if node_id is None:
        raise ValueError(
            f"{VPN_CONFIG_VAR_NODE_ID} not set in VPN configuration file"
            f" {fpath_vpn_config}"
        )

    content = (PACKAGE_DATA_DIR / ENV_EXAMPLE_FILENAME).read_text()

    content = _set_variable(content, ENV_VAR_UID, str(os.getuid()))
    content = _set_variable(content, ENV_VAR_GID, str(os.getgid()))
    content = _set_variable(content, ENV_VAR_NIPOPPY_ROOT, f"./{NIPOPPY_STUDY_DIRNAME}")
    # the node name is the same as the node ID in the VPN
    content = _set_variable(content, ENV_VAR_NODE_NAME, node_id)
    fpath_env.write_text(content)

    if copy_vpn_config:
        fpath_vpn_config_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fpath_vpn_config, fpath_vpn_config_dst)

    # contains the VPN credentials
    fpath_vpn_config_dst.chmod(0o600)
