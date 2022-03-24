import typing as t
from configparser import ConfigParser

from ..constants import CONFIG_FILE

# Define global parser
parser = ConfigParser()

# Load the config file.
parser.read(CONFIG_FILE)

# Utility function for string to boolean.
TRUE_VALUES = {"y", "yes", "t", "true", "on", "1"}
FALSE_VALUES = {"n", "no", "f", "false", "off", "0"}


def strtobool(value: str) -> bool:
    value = value.lower()

    if value in TRUE_VALUES:
        return True
    elif value in FALSE_VALUES:
        return False

    raise ValueError(f"Invalid boolean value {value}")


def config_parser(
    section: str,
    variable: str,
    cast: t.Type = str
) -> t.Any:
    if cast is bool:
        cast = strtobool

    return cast(parser.get(section, variable))
