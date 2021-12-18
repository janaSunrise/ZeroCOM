from textwrap import dedent

from .utils import config_parser, get_bright_color

# Constants.
BANNER = dedent(f"""{get_bright_color("CYAN")}
 ____               _____
/_  / ___ _______  / ___/__  __ _
 / /_/ -_) __/ _ \\/ /__/ _ \\/  ' \\
/___/\\__/_/  \\___/\\___/\\___/_/_/_/
""")

# Config file.
CONFIG_FILE = "config.ini"

# Server related config.
IP = config_parser(CONFIG_FILE, "server", "IP")
PORT = config_parser(CONFIG_FILE, "server", "port", cast_int=True)
HEADER_LENGTH = config_parser(CONFIG_FILE, "server", "HEADER_LEN", cast_int=True)
MOTD = config_parser(CONFIG_FILE, "server", "MOTD")

# Authentication config.
PASSWORD = config_parser(CONFIG_FILE, "auth", "PASSWORD")

# Max connections.
MAX_CONNECTIONS = config_parser(CONFIG_FILE, "server", "MAX_CONNECTIONS")
MAX_CONNECTIONS = None if MAX_CONNECTIONS == "" else MAX_CONNECTIONS
