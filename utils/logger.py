# -- Imports --
from datetime import datetime

from colorama import Back

from .utils import get_bright_color, get_color

# -- Log mapping --
log_mapping = {
    "error": f"[{get_bright_color('RED')}%{get_color('RESET')}]",
    "warning": f"[{get_bright_color('YELLOW')}!{get_color('RESET')}]",
    "message": f"[{get_bright_color('CYAN')}>{get_color('RESET')}]",
    "success": f"[{get_bright_color('GREEN')}+{get_color('RESET')}]",
    "info": f"[{get_bright_color('MAGENTA')}#{get_color('RESET')}]",
    "critical": f"[{get_bright_color('RED')}{Back.YELLOW}X{get_color('RESET')}{Back.RESET}]",
}


def get_logging(type_: str, date: bool = True) -> str:
    message = log_mapping[type_]

    if date:
        timestamp = datetime.now()
        timestamp = f"{get_bright_color('CYAN')}{timestamp.hour}:{timestamp.minute}:{timestamp.second}" \
                    f"{get_bright_color('RESET')}"
        message = f"[{timestamp}]{message} "

    return message


def get_message_logging(username: str, message: str, date: bool = True) -> str:
    message_log = log_mapping["message"]

    if date:
        timestamp = datetime.now()
        timestamp = f"{get_bright_color('CYAN')}{timestamp.hour}:{timestamp.minute}:{timestamp.second}" \
                    f"{get_bright_color('RESET')}"
        message = f"[{timestamp}]{get_bright_color('YELLOW')} {username} {get_color('RESET')}{message_log} " \
                  f"{get_bright_color('GREEN')}{message}"

    return message
