from datetime import datetime

from colorama import Back
from rich.console import Console

from .colors import get_bright_color, get_color


def get_log_color_mapping(color_key: str, symbol: str) -> str:
    color_map = log_color_mapping[color_key]
    return f"[{color_map}{symbol}{get_color('RESET')}]"


# Color and log type mapping
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
    "error": get_log_color_mapping("error", "%"),
    "warning": get_log_color_mapping("warning", "!"),
    "message": get_log_color_mapping("message", ">"),
    "success": get_log_color_mapping("success", "+"),
    "info": get_log_color_mapping("info", "#"),
    "critical": get_log_color_mapping("critical", "X"),
    "flash": get_log_color_mapping("flash", "-"),
}


class Logger:
    def __init__(self):
        self._console = Console()

    @staticmethod
    def _append_date(message: str) -> str:
        timestamp = datetime.now()
        timestamp = (
            f"{get_bright_color('CYAN')}"
            f"{timestamp.hour}:{timestamp.minute}:{timestamp.second}"
            f"{get_bright_color('RESET')}"
        )

        return f"[{timestamp}]{message}"

    def _print_log(self, log_type: str, message: str, date: bool = True) -> None:
        message_prefix = log_mapping[log_type]
        message = f"{message_prefix} {log_color_mapping[log_type]}{message}"

        if date:
            message = self._append_date(message)

        print(message)

    def error(self, message: str, date: bool = True) -> None:
        self._print_log("error", message, date)

    def warning(self, message: str, date: bool = True) -> None:
        self._print_log("warning", message, date)

    def success(self, message: str, date: bool = True) -> None:
        self._print_log("success", message, date)

    def info(self, message: str, date: bool = True) -> None:
        self._print_log("info", message, date)

    def critical(self, message: str, date: bool = True) -> None:
        self._print_log("critical", message, date)

    def flash(self, message: str, date: bool = True) -> None:
        self._print_log("flash", message, date)

    def message(self, username: str, user_message: str, date: bool = True, **kwargs) -> None:
        message_prefix = log_mapping["message"]
        message = f"{get_bright_color('YELLOW')} {username}{get_color('RESET')} {message_prefix} "

        if date:
            message = self._append_date(message)

        print(message, end="")
        self._console.print(user_message, **kwargs)
