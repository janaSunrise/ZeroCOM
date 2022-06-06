from textwrap import dedent

import toml

from .utils import get_bright_color

BANNER = dedent(f"""{get_bright_color("CYAN")}
 ____               _____
/_  / ___ _______  / ___/__  __ _
 / /_/ -_) __/ _ \\/ /__/ _ \\/  ' \\
/___/\\__/_/  \\___/\\___/\\___/_/_/_/
""")

# Load the `config.toml` from the root
config = toml.load("config.toml")

server_config = config["server"]["config"]

IP = server_config["ip"]
PORT = server_config["port"]
HEADER_LENGTH = server_config["header-length"]
MOTD = server_config["motd"]

PASSWORD = config["server"]["auth"]["password"]

# Load the max connections, It's `None` if 0 is specified.
MAX_CONNECTIONS = server_config["max-connections"] if server_config["max-connections"] != 0 else None
