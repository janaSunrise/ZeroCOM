import typing as t
from textwrap import dedent

from .colors import get_bright_color
from .console import clear_screen
from ..constants import VERSION


def on_startup(
    name: str,
    boot_duration: t.Optional[float] = None,
    ip: t.Optional[str] = None,
    port: t.Optional[str] = None,
    motd: t.Optional[str] = None
) -> None:
    # Imports To prevent circular imports.
    from ..config import BANNER

    # Variables
    spaces_4 = "    "

    # Generate initial message and add sections
    message = dedent(f"""{BANNER}
    {get_bright_color("GREEN")}ZeroCOM {name} Running. | {get_bright_color("YELLOW")}v{VERSION}
    """)

    if ip:
        msg = f"{spaces_4}{get_bright_color('CYAN')}Running on [IP] {ip}"
        if port:
            msg += f" | [PORT] {port}\n"
        else:
            msg += "\n"

        message += msg

    if boot_duration:
        message += f"{spaces_4}{get_bright_color('YELLOW')}TOOK {boot_duration}ms to start.\n"

    if motd:
        message += f"{spaces_4}{get_bright_color('CYAN')}MOTD: {motd}\n"

    # Clear and print screen
    clear_screen()
    print(message)
