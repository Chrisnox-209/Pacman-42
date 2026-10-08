import json
from enum import Enum
from typing import Any


class Color(Enum):
    """
    Enum representing ANSI color escape codes for terminal formatting.
    """
    BLUE = "\033[34m"
    ORANGE = "\033[38;5;208m"
    RED = "\033[31m"
    WHITE = "\033[37m"
    YELLOW = "\033[33m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RST = "\033[0m"


def check_config(file_config: str) -> Any:
    try:
        with open(file_config, "r", encoding="utf-8") as content:
            return json.load(content)
    except FileNotFoundError:
        raise ValueError(f'The file "{Color.YELLOW.value}{file_config}'
                         f'{Color.RST.value}" could not be found.')
    except json.JSONDecodeError:
        raise ValueError(f'The file "{Color.YELLOW.value}{file_config}'
                         f'"{Color.RST.value}" is not valid JSON.')


def convert_wall(nb: int) -> dict[str, int] | None:
    if nb == 0:
        return {"N": 1, "S": 1, "E": 1, "W": 1}
    elif nb == 1:
        return {"N": 0, "S": 1, "E": 1, "W": 1}
    elif nb == 2:
        return {"N": 1, "S": 1, "E": 0, "W": 1}
    elif nb == 3:
        return {"N": 0, "S": 1, "E": 0, "W": 1}
    elif nb == 4:
        return {"N": 1, "S": 0, "E": 1, "W": 1}
    elif nb == 5:
        return {"N": 0, "S": 0, "E": 1, "W": 1}
    elif nb == 6:
        return {"N": 1, "S": 0, "E": 0, "W": 1}
    elif nb == 7:
        return {"N": 0, "S": 0, "E": 0, "W": 1}
    elif nb == 8:
        return {"N": 1, "S": 1, "E": 1, "W": 0}
    elif nb == 9:
        return {"N": 0, "S": 1, "E": 1, "W": 0}
    elif nb == 10:
        return {"N": 1, "S": 1, "E": 0, "W": 0}
    elif nb == 11:
        return {"N": 0, "S": 1, "E": 0, "W": 0}
    elif nb == 12:
        return {"N": 1, "S": 0, "E": 1, "W": 0}
    elif nb == 13:
        return {"N": 0, "S": 0, "E": 1, "W": 0}
    elif nb == 14:
        return {"N": 1, "S": 0, "E": 0, "W": 0}
    elif nb == 15:
        return {"N": 0, "S": 0, "E": 0, "W": 0}
    else:
        return None


def possible_neighbor(nb: int, y: int, x: int) -> list[tuple[int, int]] | None:
    if nb == 0:
        return [(y - 1, x), (y + 1, x), (y, x + 1), (y, x - 1)]
    elif nb == 1:
        return [(y + 1, x), (y, x + 1), (y, x - 1)]
    elif nb == 2:
        return [(y - 1, x), (y + 1, x), (y, x - 1)]
    elif nb == 3:
        return [(y + 1, x), (y, x - 1)]
    elif nb == 4:
        return [(y - 1, x), (y, x + 1), (y, x - 1)]
    elif nb == 5:
        return [(y, x + 1), (y, x - 1)]
    elif nb == 6:
        return [(y - 1, x), (y, x - 1)]
    elif nb == 7:
        return [(y, x - 1)]
    elif nb == 8:
        return [(y - 1, x), (y + 1, x), (y, x + 1)]
    elif nb == 9:
        return [(y + 1, x), (y, x + 1)]
    elif nb == 10:
        return [(y - 1, x), (y + 1, x)]
    elif nb == 11:
        return [(y + 1, x)]
    elif nb == 12:
        return [(y - 1, x), (y, x + 1)]
    elif nb == 13:
        return [(y, x + 1)]
    elif nb == 14:
        return [(y - 1, x)]
    elif nb == 15:
        return None
    else:
        return None


def mirror_path(path: str | None) -> str:
    if path == "N":
        return "S"
    if path == "S":
        return "N"
    if path == "E":
        return "W"
    if path == "W":
        return "E"
    return ""
