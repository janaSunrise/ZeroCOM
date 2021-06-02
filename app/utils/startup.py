from textwrap import dedent

from .colors import get_bright_color
from .config import config_parser
from .others import clear_screen


def on_startup(
    name: str,
    boot_duration: float = None,
    ip: str = None,
    port: str = None,
    motd: str = None
) -> None:
    # Imports To prevent circular imports.
    from ..config import BANNER

    # Variables
    spaces_4 = "    "

    # Get the version
    version = config_parser("config.ini", "version", "VERSION")
    version = "v" + version if version != "" else "Version not found."

    # Generate initial message and add sections
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

    # Clear and print screen
    clear_screen()
    print(message)
