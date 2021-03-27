# -- Imports --
from textwrap import dedent

from .utils import get_bright_color, config_parser

# -- Constants --
BANNER = dedent(f"""
{get_bright_color("CYAN")}
 ____               _____
/_  / ___ _______  / ___/__  __ _ 
 / /_/ -_) __/ _ \\/ /__/ _ \\/  ' \\
/___/\\__/_/  \\___/\\___/\\___/_/_/_/
""")

CONFIG_FILE = "config.ini"
IP = config_parser(CONFIG_FILE, "server", "IP")
PORT = config_parser(CONFIG_FILE, "server", "port")
HEADER_LENGTH = config_parser(CONFIG_FILE, "server", "HEADER_LEN")
