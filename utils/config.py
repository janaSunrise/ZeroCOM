# -- Imports --
from textwrap import dedent

from .utils import config_parser, get_bright_color

# -- Constants --
BANNER = dedent(
    f"""{get_bright_color("CYAN")}
 ____               _____
/_  / ___ _______  / ___/__  __ _
 / /_/ -_) __/ _ \\/ /__/ _ \\/  ' \\
/___/\\__/_/  \\___/\\___/\\___/_/_/_/
"""
)

CONFIG_FILE = "config.ini"

IP = config_parser(CONFIG_FILE, "server", "IP")
PORT = config_parser(CONFIG_FILE, "server", "port", int_=True)
HEADER_LENGTH = config_parser(CONFIG_FILE, "server", "HEADER_LEN", int_=True)
MOTD = config_parser(CONFIG_FILE, "server", "MOTD")

PASSWORD = config_parser(CONFIG_FILE, "auth", "PASSWORD")

MAX_CONNECTIONS = config_parser(CONFIG_FILE, "server", "MAX_CONNECTIONS")
MAX_CONNECTIONS = None if MAX_CONNECTIONS == "" else MAX_CONNECTIONS
