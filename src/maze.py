"""Terminal maze renderer with Pac-Man and four ghosts."""

import curses

from mazegenerator import MazeGenerator


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

DIRECTIONS = {
    curses.KEY_UP: (0, -1, NORTH),
    curses.KEY_RIGHT: (1, 0, EAST),
    curses.KEY_DOWN: (0, 1, SOUTH),
    curses.KEY_LEFT: (-1, 0, WEST),
    ord("w"): (0, -1, NORTH),
    ord("d"): (1, 0, EAST),
    ord("s"): (0, 1, SOUTH),
    ord("a"): (-1, 0, WEST),
}


def has_wall(cell: int, wall: int) -> bool:
    """Return True if the given wall bit is present in the cell."""
    return (cell & wall) != 0


def can_move(
    maze: list[list[int]],
    x: int,
    y: int,
    wall: int,
) -> bool:
    """Return True if movement is possible from the current cell."""
    return not has_wall(maze[y][x], wall)


def find_nearest_open_cell(
    maze: list[list[int]],
    start_x: int,
    start_y: int,
) -> tuple[int, int]:
    """Find the nearest non-isolated cell from a starting position."""
    max_y = len(maze)
    max_x = len(maze[0])

    radius = 0

    while radius < max(max_x, max_y):
        for y in range(max(0, start_y - radius), min(max_y, start_y + radius + 1)):
            for x in range(max(0, start_x - radius), min(max_x, start_x + radius + 1)):
                if maze[y][x] != 15:
                    return x, y

        radius += 1

    return 0, 0


def get_start_positions(
    maze: list[list[int]],
) -> tuple[tuple[int, int], list[tuple[int, int]]]:
    """Return Pac-Man center position and four ghost corner positions."""
    height = len(maze)
    width = len(maze[0])

    pacman_start = find_nearest_open_cell(
        maze,
        width // 2,
        height // 2,
    )

    ghost_targets = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]

    ghosts = [
        find_nearest_open_cell(maze, x, y)
        for x, y in ghost_targets
    ]

    return pacman_start, ghosts


def build_maze_cells(
    maze: list[list[int]],
    pacman: tuple[int, int],
    ghosts: list[tuple[int, int]],
) -> list[list[tuple[str, int]]]:
    """Build terminal lines with color-pair information."""
    lines: list[list[tuple[str, int]]] = []
    pacman_x, pacman_y = pacman
    ghost_positions = set(ghosts)

    for y, row in enumerate(maze):
        top: list[tuple[str, int]] = []
        middle: list[tuple[str, int]] = []

        for x, cell in enumerate(row):
            top.append(("+", 0))
            top.append(("---" if has_wall(cell, NORTH) else "   ", 0))

            middle.append(("|" if has_wall(cell, WEST) else " ", 0))

            if (x, y) == (pacman_x, pacman_y):
                middle.append((" * ", 1))
            elif (x, y) in ghost_positions:
                middle.append((" # ", 2))
            else:
                middle.append(("   ", 0))

        top.append(("+", 0))
        middle.append(("|" if has_wall(row[-1], EAST) else " ", 0))

        lines.append(top)
        lines.append(middle)

    bottom: list[tuple[str, int]] = []
    for cell in maze[-1]:
        bottom.append(("+", 0))
        bottom.append(("---" if has_wall(cell, SOUTH) else "   ", 0))
    bottom.append(("+", 0))

    lines.append(bottom)

    return lines


def draw_colored_line(
    stdscr: curses.window,
    y: int,
    parts: list[tuple[str, int]],
) -> None:
    """Draw one maze line with optional colors."""
    x = 0

    for text, color_pair in parts:
        try:
            if color_pair == 0:
                stdscr.addstr(y, x, text)
            else:
                stdscr.addstr(y, x, text, curses.color_pair(color_pair))
        except curses.error:
            pass

        x += len(text)


def game(stdscr: curses.window) -> None:
    """Run the terminal maze."""
    curses.curs_set(0)
    stdscr.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)

    generator = MazeGenerator(
        size=(20, 20),
        perfect=False,
        seed=42,
    )

    maze = generator.maze
    pacman_start, ghosts = get_start_positions(maze)
    pacman_x, pacman_y = pacman_start

    while True:
        stdscr.clear()

        lines = build_maze_cells(
            maze,
            (pacman_x, pacman_y),
            ghosts,
        )

        for index, line in enumerate(lines):
            draw_colored_line(stdscr, index, line)

        help_line = len(lines) + 1

        try:
            stdscr.addstr(help_line, 0, "* = Pac-Man | # = Ghost | Move: arrows/WASD | Quit: Q")
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break

        movement = DIRECTIONS.get(key)

        if movement is None:
            continue

        dx, dy, wall = movement

        if can_move(maze, pacman_x, pacman_y, wall):
            next_x = pacman_x + dx
            next_y = pacman_y + dy

            if (
                0 <= next_y < len(maze)
                and 0 <= next_x < len(maze[0])
                and maze[next_y][next_x] != 15
            ):
                pacman_x = next_x
                pacman_y = next_y
