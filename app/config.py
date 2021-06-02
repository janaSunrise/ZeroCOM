# -- Imports --
from textwrap import dedent

from colorama import Back

from .utils import config_parser, get_color, get_bright_color

# -- Constants --
BANNER = dedent(f"""{get_bright_color("CYAN")}
 ____               _____
/_  / ___ _______  / ___/__  __ _
 / /_/ -_) __/ _ \\/ /__/ _ \\/  ' \\
/___/\\__/_/  \\___/\\___/\\___/_/_/_/
""")

CONFIG_FILE = "config.ini"

IP = config_parser(CONFIG_FILE, "server", "IP")
PORT = config_parser(CONFIG_FILE, "server", "port", int_=True)
HEADER_LENGTH = config_parser(CONFIG_FILE, "server", "HEADER_LEN", int_=True)
MOTD = config_parser(CONFIG_FILE, "server", "MOTD")

PASSWORD = config_parser(CONFIG_FILE, "auth", "PASSWORD")

MAX_CONNECTIONS = config_parser(CONFIG_FILE, "server", "MAX_CONNECTIONS")
MAX_CONNECTIONS = None if MAX_CONNECTIONS == "" else MAX_CONNECTIONS

# -- Mappings --
log_color_mapping = {
    "error": get_bright_color("RED"),
    "warning": get_bright_color("YELLOW"),
    "message": get_color("CYAN"),
    "success": get_bright_color("GREEN"),
    "info": get_bright_color("MAGENTA"),
    "critical": get_bright_color("RED") + Back.YELLOW,
    "flash": get_bright_color("BLUE"),
}

log_mapping = {
    "error": f"[{log_color_mapping['error']}%{get_color('RESET')}]",
    "warning": f"[{log_color_mapping['warning']}!{get_color('RESET')}]",
    "message": f"[{log_color_mapping['message']}>{get_color('RESET')}]",
    "success": f"[{log_color_mapping['success']}+{get_color('RESET')}]",
    "info": f"[{log_color_mapping['info']}#{get_color('RESET')}]",
    "critical": f"[{log_color_mapping['critical']}X{get_color('RESET')}{Back.RESET}]",
    "flash": f"[{log_color_mapping['flash']}-{get_color('RESET')}]",
}
