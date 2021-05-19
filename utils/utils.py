import os
import typing as t
from configparser import SafeConfigParser
from textwrap import dedent

import colorama

colorama.init(autoreset=True)


def get_color(color: str) -> str:
    return getattr(colorama.Fore, color.upper())


def get_bright_color(color: str) -> str:
    return getattr(colorama.Style, "BRIGHT") + get_color(color)  # noqa: B009


def clear_screen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def config_parser(
    filename: str, section: str, variable: str, bool_: bool = False, int_: bool = False
) -> t.Any:
    parser = SafeConfigParser()
    parser.read(filename)

    if bool_:
        return parser.getboolean(section, variable)
    elif int_:
        return parser.getint(section, variable)
    else:
        return parser.get(section, variable)


def on_startup(
    name: str, boot_duration: float = None, ip: str = None, port: str = None, motd: str = None
) -> None:
    from .config import BANNER  # To prevent circular imports.

    spaces_4 = "    "

    version = config_parser("config.ini", "version", "VERSION")
    version = "v" + version if version != "" else "Version not found."

    clear_screen()

    message = dedent(f"""{BANNER}
    {get_bright_color("GREEN")}ZeroCOM {name} Running. | {get_bright_color("YELLOW")}{version}
    """)

    if ip is not None:
        msg = f"{spaces_4}{get_bright_color('CYAN')}Running on [IP] {ip}"
        if port is not None:
            msg += f" | [PORT] {port}\n"
        else:
            msg += "\n"

        message += msg

    if boot_duration is not None:
        message += f"{spaces_4}{get_bright_color('YELLOW')}TOOK {boot_duration}ms to start.\n"

    if motd is not None:
        message += f"{spaces_4}{get_bright_color('CYAN')}MOTD: {motd}\n"

    print(message)
