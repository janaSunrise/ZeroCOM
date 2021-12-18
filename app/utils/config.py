import typing as t
from configparser import ConfigParser


def config_parser(
    filename: str,
    section: str,
    variable: str,
    cast_bool: bool = False,
    cast_int: bool = False
) -> t.Any:
    parser = ConfigParser()
    parser.read(filename)

    if cast_bool:
        return parser.getboolean(section, variable)
    elif cast_int:
        return parser.getint(section, variable)
    else:
        return parser.get(section, variable)
