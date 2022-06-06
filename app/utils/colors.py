import colorama

colorama.init(autoreset=True)


def get_color(color: str) -> str:
    return getattr(colorama.Fore, color.upper())


def get_bright_color(color: str) -> str:
    return colorama.Style.BRIGHT + get_color(color)
