import os
from textwrap import dedent

import toml

# Hard-coded constants
VERSION = "0.1.0"
BANNER = dedent(
    """
 ____               _____
/_  / ___ _______  / ___/__  __ _
 / /_/ -_) __/ _ \\/ /__/ _ \\/  ' \\
/___/\\__/_/  \\___/\\___/\\___/_/_/_/
"""
)

# Logging setting
DEBUG = bool(os.environ.get("ZEROCOM_DEBUG", 0))
LOG_FILE = os.environ.get("ZEROCOM_LOG_FILE", None)
LOG_FILE_MAX_SIZE = int(os.environ.get("ZEROCOM_LOG_FILE_SIZE_MAX", 1_048_576))  # in bytes (default: 1MiB)

# Config file location, in this case it's `config.toml` in root
CONFIG_FILE = os.environ.get("ZEROCOM_CONFIG_FILE", "config.toml")
config = toml.load(CONFIG_FILE)
server_config = config["server"]["config"]


class Config:
    IP = server_config["ip"]
    PORT = server_config["port"]
    MOTD = server_config["motd"]

    PASSWORD = config["server"]["auth"]["password"]

    # Load the max connections, It's `None` if 0 is specified.
    MAX_CONNECTIONS = server_config["max-connections"] if server_config["max-connections"] != 0 else None
