"""Handle wall masks, pellet placement, and terminal colors."""

from enum import Enum
import random


class Color(Enum):
    """Represent ANSI color escape codes for terminal messages."""

    BLUE = "\033[1;34m"
    ORANGE = "\033[38;5;208m"
    RED = "\033[31m"
    WHITE = "\033[37m"
    YELLOW = "\033[33m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RST = "\033[0m"


def convert_wall(nb: int) -> dict[str, int] | None:
    """Return open directions for a wall mask, or None if invalid."""
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
    """Return accessible (row, column) neighbors, or None."""
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
    """Return the opposite direction, or an empty string if unknown."""
    if path == "N":
        return "S"
    if path == "S":
        return "N"
    if path == "E":
        return "W"
    if path == "W":
        return "E"
    return ""


def time_game(remaining_time: int) -> int:
    """Decrease a positive timer by one and return its value."""
    if remaining_time > 0:
        remaining_time -= 1
    return remaining_time


def find_player_spawn(maze: list[list[int]]) -> tuple[int, int]:
    """Return an open cell near the center as (x, y).

    Raise ValueError if the maze contains no valid spawn cell.
    """
    height: int = len(maze)
    width: int = len(maze[0])

    center_x: int = width // 2
    center_y: int = height // 2

    for radius in range(max(width, height)):
        for y in range(
            max(0, center_y - radius),
            min(height, center_y + radius + 1),
        ):
            for x in range(
                max(0, center_x - radius),
                min(width, center_x + radius + 1),
            ):
                if maze[y][x] != 15:
                    return x, y

    raise ValueError("No valid player spawn found.")


def generate_pacgum(maze: list[list[int]],
                    percentage_pacgum: int) -> dict[tuple[int, int], bool]:
    """Place pellets randomly outside the spawn and corner cells.

    Return presence flags keyed by (row, column) coordinates.
    """
    player_x: int
    player_y: int

    list_packgum: dict[tuple[int, int], bool] = {}
    free_cases: list[tuple[int, int]] = []

    height: int = len(maze)
    width: int = len(maze[0])

    player_x, player_y = find_player_spawn(maze)
    corners_and_player: set[tuple[int, int]] = {
        (0, 0),
        (0, width - 1),
        (height - 1, 0),
        (height - 1, width - 1),
        (player_y, player_x)
    }

    for y in range(height):
        for x in range(len(maze[y])):

            list_packgum[(y, x)] = False

            if maze[y][x] != 15 and (y, x) not in corners_and_player:
                free_cases.append((y, x))

    quantity: int = len(free_cases) * percentage_pacgum // 100

    result: list[tuple[int, int]] = random.sample(
        free_cases, quantity
    )

    for position in result:
        list_packgum[position] = True

    return list_packgum


def generate_super_pacgum(maze: list[list[int]]
                          ) -> dict[tuple[int, int], bool]:
    """Return presence flags for power pellets at the four corners."""
    height: int = len(maze)
    width: int = len(maze[0])

    list_super_packgum: dict[tuple[int, int], bool] = {
        (0, 0): True,
        (0, width - 1): True,
        (height - 1, 0): True,
        (height - 1, width - 1): True
    }
    return list_super_packgum
