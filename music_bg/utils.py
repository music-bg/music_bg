import os
from pathlib import Path


def xdg_config_home() -> Path:
    """
    Return a Path corresponding to XDG_CONFIG_HOME.

    :return: xdg_config_home path.
    """
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if not config_home:
        return Path.home() / ".config"
    return Path(config_home)
