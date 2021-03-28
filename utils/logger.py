# -- Imports --
from datetime import datetime

from colorama import Back

from .utils import get_bright_color, get_color

# -- Log mapping --
log_color_mapping = {
    "error": get_bright_color('RED'),
    "warning": get_bright_color('YELLOW'),
    "message": get_bright_color('CYAN'),
    "success": get_bright_color('GREEN'),
    "info": get_bright_color('MAGENTA'),
    "critical": get_bright_color('RED') + Back.YELLOW
}

log_mapping = {
    "error": f"[{log_color_mapping['error']}%{get_color('RESET')}]",
    "warning": f"[{log_color_mapping['warning']}!{get_color('RESET')}]",
    "message": f"[{log_color_mapping['message']}>{get_color('RESET')}]",
    "success": f"[{log_color_mapping['success']}+{get_color('RESET')}]",
    "info": f"[{log_color_mapping['info']}#{get_color('RESET')}]",
    "critical": f"[{log_color_mapping['critical']}X{get_color('RESET')}{Back.RESET}]",
}


def get_logging(type_: str, log_message: str, date: bool = True) -> str:
    message = log_mapping[type_]

    if date:
        timestamp = datetime.now()
        timestamp = f"{get_bright_color('CYAN')}{timestamp.hour}:{timestamp.minute}:{timestamp.second}" \
                    f"{get_bright_color('RESET')}"
        message = f"[{timestamp}]{message} {log_color_mapping[type_]}{log_message}"

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
