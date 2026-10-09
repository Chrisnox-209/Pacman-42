from typing import TYPE_CHECKING

from mazegenerator import MazeGenerator

from src.algorithm import (
    bfs,
    move_randomly,
    preshoot,
    to_flee,
    unpredictable,
)
from src.ghost import Ghost
from src.game import Player, GameState
from src.parse import ParseConfig, LevelConfig

if TYPE_CHECKING:
    from src.ui import GameWindow

import curses
import time


def find_player_spawn(
    maze: list[list[int]],
) -> tuple[int, int]:
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


def move_player(
    maze: list[list[int]],
    player: Player,
    key: int,
) -> None:
    wall: int = maze[player.y][player.x]

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
    stdscr: "GameWindow",
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
) -> None:
    from src.ui import draw_maze, setup_terminal

    setup_terminal(stdscr)

    last_paths: dict[str, str | None] = {
        "Athos": None,
        "Porthos": None,
        "Aramis": None,
        "Dartagnan": None,
    }

    last_positions: dict[str, tuple[int, int] | None] = {
        "Athos": None,
        "Porthos": None,
        "Aramis": None,
        "Dartagnan": None,
    }

    while not game_state.game_over:
        key: int = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break

        move_player(
            maze,
            player,
            key,
        )

        if game_state.frightened:
            for ghost in ghosts:
                start: tuple[int, int] = (
                    ghost.y,
                    ghost.x,
                )
                target: tuple[int, int] = (
                    player.y,
                    player.x,
                )

                if start == target:
                    ghosts.remove(ghost)
                    continue

                next_pos: tuple[int, int] = to_flee(
                    start,
                    target,
                    last_positions[ghost.name],
                    maze,
                )

                last_positions[ghost.name] = start
                ghost.move_to_position(next_pos)

        else:
            for ghost in ghosts:
                start = (
                    ghost.y,
                    ghost.x,
                )

                position_player: tuple[int, int] = (
                    player.y,
                    player.x,
                )

                if start == position_player:
                    ghosts.remove(ghost)
                    continue

                if ghost.name == "Athos":
                    road: list[tuple[int, int]] = bfs(
                        start,
                        position_player,
                        maze,
                    )

                    if len(road) > 1:
                        ghost.move_to_position(road[1])

                elif ghost.name == "Porthos":
                    target = preshoot(
                        position_player,
                        maze,
                    )

                    road = bfs(
                        start,
                        target,
                        maze,
                    )

                    if len(road) > 1:
                        ghost.move_to_position(road[1])

                elif ghost.name == "Dartagnan":
                    next_pos = unpredictable(
                        start,
                        position_player,
                        maze,
                    )

                    ghost.move_to_position(next_pos)

                else:
                    path: dict[str, int] | None = (
                        ghost.check_path(maze)
                    )

                    if path is None:
                        continue

                    direction: str | None = move_randomly(
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


def create_game(config: ParseConfig
                ) -> tuple[list[list[int]], Player, list[Ghost], GameState]:

    game_state = GameState(
        score=0,
        level=1,
        remaining_time=90,
        frightened=False,
        game_over=False,
        cheat=False,
    )

    level_index: int = game_state.level - 1
    level: LevelConfig = config.levels[level_index]

    generator = MazeGenerator(
        size=(level.width, level.width),
        perfect=config.perfect,
        seed=config.seed,
    )

    maze: list[list[int]] = generator.maze

    player_x: int
    player_y: int
    player_x, player_y = find_player_spawn(maze)

    player = Player(
        x=player_x,
        y=player_y,
        spawn_position=(player_x, player_y),
        direction=(1, 0),
        lives=3,
    )

    height: int = len(maze) - 1
    width: int = len(maze[0]) - 1

    ghosts: list[Ghost] = [
        Ghost(0, 0, (0, 0), "Athos"),
        Ghost(width, 0, (width, 0), "Porthos"),
        Ghost(0, height, (0, height), "Aramis"),
        Ghost(
            width,
            height,
            (width, height),
            "Dartagnan",
        ),
    ]

    return maze, player, ghosts, game_state
