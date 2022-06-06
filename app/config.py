from textwrap import dedent

import toml

# Version for the app
VERSION = "0.1.0"

# Banner to be displayed when the server is run
BANNER = dedent("""
 ____               _____
/_  / ___ _______  / ___/__  __ _
 / /_/ -_) __/ _ \\/ /__/ _ \\/  ' \\
/___/\\__/_/  \\___/\\___/\\___/_/_/_/
""")

# Config file location, in this case it's `config.toml` in root
CONFIG_FILE = "config.toml"
config = toml.load(CONFIG_FILE)

server_config = config["server"]["config"]


class Config:
    IP = server_config["ip"]
    PORT = server_config["port"]
    HEADER_LENGTH = server_config["header-length"]
    MOTD = server_config["motd"]

    PASSWORD = config["server"]["auth"]["password"]

    # Load the max connections, It's `None` if 0 is specified.
    MAX_CONNECTIONS = server_config["max-connections"] if server_config["max-connections"] != 0 else None
