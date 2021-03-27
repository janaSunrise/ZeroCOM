# -- Imports --
from datetime import datetime

from .utils import get_bright_color, get_color

# -- Log mapping --
log_mapping = {
    "error": f"[{get_bright_color('RED')}X{get_color('RESET')}]",
    "warning": f"[{get_bright_color('YELLOW')}!{get_color('RESET')}]",
    "message": f"[{get_bright_color('CYAN')}>{get_color('RESET')}]",
    "success": f"[{get_bright_color('GREEN')}+{get_color('RESET')}]",
}

def get_logging(type_: str, date: bool = False) -> str:
    message = log_mapping[type_]

    if date:
        timestamp = datetime.now()
        timestamp = f"{timestamp.hour}:{timestamp.minute}:{timestamp.second}"
        message = f"[{timestamp}]" + message

    return message
