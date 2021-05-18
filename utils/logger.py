# -- Imports --
from datetime import datetime

from colorama import Back

from .utils import get_bright_color, get_color

# -- Log mapping --
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


class Logger:
    @staticmethod
    def _append_date(message: str):
        timestamp = datetime.now()
        timestamp = (
            f"{get_bright_color('CYAN')}"
            f"{timestamp.hour}:{timestamp.minute}:{timestamp.second}"
            f"{get_bright_color('RESET')}"
        )

        return f"{get_bright_color('WHITE')}[{timestamp}]{message}"

    def error(self, message: str, date: bool = True):
        log_type = "error"

        message_prefix = log_mapping[log_type]

        message = f"{message_prefix} {log_color_mapping[log_type]}{message}"
        if date:
            message = self._append_date(message)

        print(message)

    def warning(self, message: str, date: bool = True):
        log_type = "warning"

        message_prefix = log_mapping[log_type]

        message = f"{message_prefix} {log_color_mapping[log_type]}{message}"
        if date:
            message = self._append_date(message)

        print(message)

    def message(self, username: str, message: str, date: bool = True, **kwargs):
        log_type = "message"

        message_prefix = log_mapping[log_type]

        message = (
            f"{get_bright_color('YELLOW')} {username} {get_color('RESET')}{message_prefix} "
            f"{get_bright_color('CYAN')}{message}"
        )

        if date:
            message = self._append_date(message)

        print(message, **kwargs)

    def success(self, message: str, date: bool = True):
        log_type = "success"

        message_prefix = log_mapping[log_type]

        message = f"{message_prefix} {log_color_mapping[log_type]}{message}"
        if date:
            message = self._append_date(message)

        print(message)

    def info(self, message: str, date: bool = True):
        log_type = "info"

        message_prefix = log_mapping[log_type]

        message = f"{message_prefix} {log_color_mapping[log_type]}{message}"
        if date:
            message = self._append_date(message)

        print(message)

    def critical(self, message: str, date: bool = True):
        log_type = "critical"

        message_prefix = log_mapping[log_type]

        message = f"{message_prefix} {log_color_mapping[log_type]}{message}"
        if date:
            message = self._append_date(message)

        print(message)

    def flash(self, message: str, date: bool = True):
        log_type = "flash"

        message_prefix = log_mapping[log_type]

        message = f"{message_prefix} {log_color_mapping[log_type]}{message}"
        if date:
            message = self._append_date(message)

        print(message)
