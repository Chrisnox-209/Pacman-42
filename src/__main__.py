from src.algorithm import bfs
from src.game import GameState, Player
from src.ghost import Ghost
from src.maze import draw_maze, setup_terminal
from mazegenerator import MazeGenerator
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
    player: Player,
    key: int,
) -> None:
    wall = maze[player.y][player.x]

    if key in (curses.KEY_UP, ord("w")):
        if wall & 1 == 0:
            player.y -= 1
            player.direction = (0, -1)

    elif key in (curses.KEY_RIGHT, ord("d")):
        if wall & 2 == 0:
            player.x += 1
            player.direction = (1, 0)

    elif key in (curses.KEY_DOWN, ord("s")):
        if wall & 4 == 0:
            player.y += 1
            player.direction = (0, 1)

    elif key in (curses.KEY_LEFT, ord("a")):
        if wall & 8 == 0:
            player.x -= 1
            player.direction = (-1, 0)


def run(
    stdscr: curses.window,
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
) -> None:
    setup_terminal(stdscr)

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

        move_player(
            maze,
            player,
            key,
        )

        for ghost in ghosts:
            if ghost.name == "Athos":
                start: tuple[int, int] = (ghost.y, ghost.x)
                target: tuple[int, int] = (player.y, player.x)

                route: list[tuple[int, int]] = bfs(
                    start,
                    target,
                    maze,
                )

                if len(route) > 1:
                    ghost.move_to_position(route[1])

            else:
                path: dict[str, int] | None = ghost.check_path(maze)

                if path is None:
                    continue

                direction: str | None = ghost.move(
                    path,
                    last_paths[ghost.name],
                )

                if direction is not None:
                    ghost.move_to_direction(direction)
                    last_paths[ghost.name] = direction

        draw_maze(
            stdscr,
            maze,
            player,
            ghosts,
            game_state,
        )

        time.sleep(0.3)


def main() -> None:
    generator = MazeGenerator(
        size=(20, 20),
        perfect=False,
        seed=42,
    )

    maze: list[list[int]] = generator.maze

    player_x, player_y = find_player_spawn(maze)

    player = Player(
        x=player_x,
        y=player_y,
        spawn_position=(player_x, player_y),
        direction=(1, 0),
        lives=3,
    )

    game_state = GameState(
        score=0,
        level=1,
        remaining_time=90,
        frightened=False,
        game_over=False,
        cheat=False,
    )

    ghosts: list[Ghost] = [
        Ghost(0, 0, (0, 0), "Athos"),
        Ghost(19, 0, (19, 0), "Porthos"),
        Ghost(0, 19, (0, 19), "Aramis"),
        Ghost(19, 19, (19, 19), "Dartagnan"),
    ]

    curses.wrapper(
        run,
        maze,
        player,
        ghosts,
        game_state,
    )


if __name__ == "__main__":
    main()
