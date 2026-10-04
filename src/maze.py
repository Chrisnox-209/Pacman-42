from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import GameState, Player
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
    """Return the terminal symbol associated with a ghost."""
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
    """Return the curses style associated with the player."""
    if not curses.has_colors():
        return curses.A_BOLD

    return curses.color_pair(PLAYER_COLOR) | curses.A_BOLD


def required_terminal_size(
    maze: list[list[int]],
    ghosts: list[Ghost],
) -> tuple[int, int]:
    """Return the minimum terminal height and width for the display."""
    maze_height = len(maze)
    maze_width = len(maze[0])

    required_height = (maze_height * 2) + len(ghosts) + 6
    required_width = (maze_width * CELL_WIDTH) + 1

    return required_height, required_width


def show_resize_message(
    stdscr: curses.window,
    required_height: int,
    required_width: int,
) -> None:
    """Display a resize message instead of crashing curses."""
    current_height, current_width = stdscr.getmaxyx()

    stdscr.erase()

    message = (
        f"Terminal too small: {current_width}x{current_height}. "
        f"Required: {required_width}x{required_height}."
    )

    max_length = max(1, current_width - 1)

    try:
        stdscr.addnstr(0, 0, message, max_length)
        stdscr.addnstr(
            1,
            0,
            "Resize the terminal or press Q to quit.",
            max_length,
        )
    except curses.error:
        pass

    stdscr.noutrefresh()
    curses.doupdate()


def draw_maze(
    stdscr: curses.window,
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
) -> None:

    """Draw the current test state without changing game logic."""
    if not maze or not maze[0]:
        raise ValueError("Maze cannot be empty.")

    width = len(maze[0])

    if any(len(maze_row) != width for maze_row in maze):
        raise ValueError("Maze rows must all have the same width.")

    required_height, required_width = required_terminal_size(
        maze,
        ghosts,
    )
    terminal_height, terminal_width = stdscr.getmaxyx()

    if (
        terminal_height < required_height
        or terminal_width < required_width
    ):
        show_resize_message(
            stdscr,
            required_height,
            required_width,
        )
        return

    ghost_positions: dict[tuple[int, int], Ghost] = {
        (ghost.x, ghost.y): ghost
        for ghost in ghosts
    }

    stdscr.erase()
    row = 0

    for y, maze_row in enumerate(maze):
        col = 0

        for cell in maze_row:
            stdscr.addstr(row, col, "+")

            if cell & NORTH:
                stdscr.addstr(row, col + 1, "---")
            else:
                stdscr.addstr(row, col + 1, "   ")

            col += CELL_WIDTH

        stdscr.addstr(row, col, "+")
        row += 1
        col = 0

        for x, cell in enumerate(maze_row):
            if cell & WEST:
                stdscr.addstr(row, col, "|")
            else:
                stdscr.addstr(row, col, " ")

            stdscr.addstr(row, col + 1, "   ")

            if (x, y) == (player.x, player.y):
                stdscr.addstr(
                    row,
                    col + 2,
                    "*",
                    get_player_style(),
                )
            else:
                ghost = ghost_positions.get((x, y))

                if ghost is not None:
                    stdscr.addstr(
                        row,
                        col + 2,
                        get_ghost_symbol(ghost.name),
                        get_ghost_style(ghost.name),
                    )

            col += CELL_WIDTH

        if maze_row[-1] & EAST:
            stdscr.addstr(row, col, "|")
        else:
            stdscr.addstr(row, col, " ")

        row += 1

    col = 0

    for cell in maze[-1]:
        stdscr.addstr(row, col, "+")

        if cell & SOUTH:
            stdscr.addstr(row, col + 1, "---")
        else:
            stdscr.addstr(row, col + 1, "   ")

        col += CELL_WIDTH

    stdscr.addstr(row, col, "+")
    row += 2

    stdscr.addstr(
        row,
        0,
        (
            f"Score: {game_state.score} | "
            f"Level: {game_state.level} | "
            f"Time: {game_state.remaining_time} | "
            f"Frightened: {game_state.frightened} | "
            f"Game over: {game_state.game_over} | "
            f"Cheat: {game_state.cheat}"
        ),
    )
    row += 1

    stdscr.addstr(
        row,
        0,
        (
            f"Player ({player.x}, {player.y}) | "
            f"Lives: {player.lives} | "
            f"Direction: {player.direction}"
        ),
    )
    row += 1

    for ghost in ghosts:
        stdscr.addstr(
            row,
            0,
            f"{ghost.name:<10} ({ghost.x}, {ghost.y})",
        )
        row += 1

    stdscr.addstr(
        row + 1,
        0,
        "Arrows / WASD: move player | Q: quit",
    )

    stdscr.noutrefresh()
    curses.doupdate()
