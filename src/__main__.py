from src.maze import draw_maze, setup_terminal
from src.ghost import Ghost
from mazegenerator import MazeGenerator
from src.algorithm import bfs
import curses
import time


def find_player_spawn(
    maze: list[list[int]],
) -> tuple[int, int]:
    height = len(maze)
    width = len(maze[0])

    center_x = width // 2
    center_y = height // 2

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


def move_player(
    maze: list[list[int]],
    player: tuple[int, int],
    key: int,
) -> tuple[int, int]:
    x, y = player
    wall = maze[y][x]

    if key in (curses.KEY_UP, ord("w")):
        if wall & 1 == 0:
            y -= 1

    elif key in (curses.KEY_RIGHT, ord("d")):
        if wall & 2 == 0:
            x += 1

    elif key in (curses.KEY_DOWN, ord("s")):
        if wall & 4 == 0:
            y += 1

    elif key in (curses.KEY_LEFT, ord("a")):
        if wall & 8 == 0:
            x -= 1

    return x, y


def run(
    stdscr: curses.window,
    maze: list[list[int]],
    ghosts: list[Ghost],
) -> None:
    setup_terminal(stdscr)

    player: tuple[int, int] = find_player_spawn(maze)

    last_paths: dict[str, str | None] = {
        "Athos": None,
        "Porthos": None,
        "Aramis": None,
        "Dartagnan": None,
    }

    while True:
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break

        player = move_player(
            maze,
            player,
            key,
        )

        for ghost in ghosts:
            
            if ghost.name == "Athos":
                start = (ghost.y, ghost.x)
                target = (player[1], player[0])
                route = bfs(start, target, maze)
                ghost.move_to_position(route[1])
            else:
                path = ghost.check_path(maze)

                if path is None:
                    continue

                direction = ghost.move(
                    path,
                    last_paths[ghost.name],
                )

                if direction is not None:
                    ghost.move_to_direction(direction)
                    last_paths[ghost.name] = direction

        draw_maze(
            stdscr,
            maze,
            ghosts,
            player,
        )
        time.sleep(0.3)


def main() -> None:
    generator = MazeGenerator(
        size=(20, 20),
        perfect=False,
        seed=42,
    )

    maze: list[list[int]] = generator.maze

    ghosts: list[Ghost] = [
        Ghost(0, 0, (0, 0), "Athos"),
        Ghost(19, 0, (19, 0), "Porthos"),
        Ghost(0, 19, (0, 19), "Aramis"),
        Ghost(19, 19, (19, 19), "Dartagnan"),
    ]



    curses.wrapper(
        run,
        maze,
        ghosts,
    )

    # bfs((0, 0), (18, 18), maze)


if __name__ == "__main__":
    main()