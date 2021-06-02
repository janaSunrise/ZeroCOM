import typing as t
from configparser import ConfigParser


def config_parser(
    filename: str,
    section: str,
    variable: str,
    bool_: bool = False,
    int_: bool = False
) -> t.Any:
    parser = ConfigParser()
    parser.read(filename)

    if bool_:
        return parser.getboolean(section, variable)
    elif int_:
        return parser.getint(section, variable)
    else:
        return parser.get(section, variable)
