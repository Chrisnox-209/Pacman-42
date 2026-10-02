from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ghost import Ghost


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

CELL_WIDTH = 4

PLAYER_COLOR = 5

GHOST_COLORS: dict[str, int] = {
    "Athos": 1,
    "Porthos": 2,
    "Aramis": 3,
    "Dartagnan": 4,
}


def setup_terminal(stdscr: curses.window) -> None:
    """Configure curses for the terminal test display."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    stdscr.leaveok(True)

    if not curses.has_colors():
        return

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_GREEN, -1)
    curses.init_pair(PLAYER_COLOR, curses.COLOR_YELLOW, -1)


def get_ghost_symbol(name: str) -> str:
    """Return a short terminal symbol for a ghost."""
    symbols: dict[str, str] = {
        "Athos": "A",
        "Porthos": "P",
        "Aramis": "R",
        "Dartagnan": "D",
    }

    if name in symbols:
        return symbols[name]

    if name:
        return name[0].upper()

    return "G"


def get_ghost_style(name: str) -> int:
    """Return the curses style associated with a ghost."""
    if not curses.has_colors():
        return curses.A_BOLD

    color_id = GHOST_COLORS.get(name)

    if color_id is None:
        return curses.A_BOLD

    return curses.color_pair(color_id) | curses.A_BOLD


def get_player_style() -> int:
    """Return the curses style used for the player."""
    if not curses.has_colors():
        return curses.A_BOLD

    return curses.color_pair(PLAYER_COLOR) | curses.A_BOLD


def draw_horizontal_wall(
    stdscr: curses.window,
    row: int,
    col: int,
    cell: int,
) -> int:
    """Draw the north wall of one maze cell."""
    stdscr.addstr(row, col, "+")

    if cell & NORTH:
        stdscr.addstr(row, col + 1, "---")
    else:
        stdscr.addstr(row, col + 1, "   ")

    return col + CELL_WIDTH


def draw_cell(
    stdscr: curses.window,
    row: int,
    col: int,
    cell: int,
    ghost: Ghost | None,
    is_player: bool,
) -> int:
    """Draw one maze cell and its optional entity."""
    if cell & WEST:
        stdscr.addstr(row, col, "|")
    else:
        stdscr.addstr(row, col, " ")

    stdscr.addstr(row, col + 1, "   ")

    if is_player:
        stdscr.addstr(
            row,
            col + 2,
            "*",
            get_player_style(),
        )
    elif ghost is not None:
        stdscr.addstr(
            row,
            col + 2,
            get_ghost_symbol(ghost.name),
            get_ghost_style(ghost.name),
        )

    return col + CELL_WIDTH


def draw_bottom_wall(
    stdscr: curses.window,
    row: int,
    maze: list[list[int]],
) -> None:
    """Draw the south border of the maze."""
    width = len(maze[0])
    col = 0

    for x in range(width):
        cell = maze[-1][x]

        stdscr.addstr(row, col, "+")

        if cell & SOUTH:
            stdscr.addstr(row, col + 1, "---")
        else:
            stdscr.addstr(row, col + 1, "   ")

        col += CELL_WIDTH

    stdscr.addstr(row, col, "+")


def draw_status(
    stdscr: curses.window,
    start_row: int,
    player: tuple[int, int],
    ghosts: list[Ghost],
) -> None:
    """Display player and ghost coordinates below the maze."""
    player_x, player_y = player

    stdscr.addstr(
        start_row,
        0,
        f"Player     ({player_x:>2}, {player_y:>2})",
    )

    row = start_row + 1

    for ghost in ghosts:
        stdscr.addstr(
            row,
            0,
            f"{ghost.name:<10} ({ghost.x:>2}, {ghost.y:>2})",
        )
        row += 1

    stdscr.addstr(
        row + 1,
        0,
        "Arrows / WASD: move player | Q: quit",
    )


def draw_maze(
    stdscr: curses.window,
    maze: list[list[int]],
    ghosts: list[Ghost],
    player: tuple[int, int],
) -> None:
    """Draw maze, ghosts and player without updating game state."""
    if not maze:
        raise ValueError("Maze cannot be empty.")

    if not maze[0]:
        raise ValueError("Maze rows cannot be empty.")

    width = len(maze[0])

    if any(len(row) != width for row in maze):
        raise ValueError("Maze rows must all have the same width.")

    player_x, player_y = player

    ghost_positions: dict[tuple[int, int], Ghost] = {
        (ghost.x, ghost.y): ghost
        for ghost in ghosts
    }

    row = 0

    for y, maze_row in enumerate(maze):
        col = 0

        for cell in maze_row:
            col = draw_horizontal_wall(
                stdscr,
                row,
                col,
                cell,
            )

        stdscr.addstr(row, col, "+")
        row += 1
        col = 0

        for x, cell in enumerate(maze_row):
            ghost = ghost_positions.get((x, y))

            col = draw_cell(
                stdscr,
                row,
                col,
                cell,
                ghost,
                (x, y) == (player_x, player_y),
            )

        last_cell = maze_row[-1]

        if last_cell & EAST:
            stdscr.addstr(row, col, "|")
        else:
            stdscr.addstr(row, col, " ")

        row += 1

    draw_bottom_wall(stdscr, row, maze)
    draw_status(stdscr, row + 2, player, ghosts)

    stdscr.noutrefresh()
    curses.doupdate()
