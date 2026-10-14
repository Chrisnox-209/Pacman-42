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
from src.utils import (time_game, generate_pacgum,
                       find_player_spawn, generate_super_pacgum)

if TYPE_CHECKING:
    from src.ui import GameWindow

import curses
import time


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
    config: ParseConfig,
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

    last_time: float = time.monotonic()
    movement_key: int = -1

    while not game_state.game_over:
        key: int = stdscr.getch()

        current_time: float = time.monotonic()

        if current_time - last_time >= 1:
            game_state.remaining_time = time_game(
                game_state.remaining_time
            )
            last_time = current_time

        if game_state.remaining_time == 0:
            game_state.game_over = True
            return

        if key in (ord("q"), ord("Q")):
            return

        if key in (
            curses.KEY_UP,
            curses.KEY_RIGHT,
            curses.KEY_DOWN,
            curses.KEY_LEFT,
            ord("w"),
            ord("d"),
            ord("s"),
            ord("a"),
        ):
            movement_key = key

        move_player(
            maze,
            player,
            movement_key,
        )

        position_player: tuple[int, int] = (
            player.y,
            player.x,
        )

        for key in game_state.position_super_pacgum:
            if (position_player == key and
               game_state.position_super_pacgum[key]):

                game_state.score = (game_state.score +
                                    config.points_per_super_pacgum)

        for key in game_state.position_pacgum:
            if position_player == key and game_state.position_pacgum[key]:
                game_state.score = (game_state.score +
                                    config.points_per_pacgum)
            if position_player == key:
                game_state.position_pacgum[key] = False

        if (any(game_state.position_pacgum.values()) is not True and
           any(game_state.position_super_pacgum.values) is not True):
            game_state.level += 1
            game_state.victory = True
            return

        if game_state.frightened:
            for ghost in ghosts:
                start: tuple[int, int] = (
                    ghost.y,
                    ghost.x,
                )

                if start == position_player:
                    game_state.game_over = True
                    break

                next_pos: tuple[int, int] = to_flee(
                    start,
                    position_player,
                    last_positions[ghost.name],
                    maze,
                )

                last_positions[ghost.name] = start
                ghost.move_to_position(next_pos)

                if (ghost.y, ghost.x) == position_player:
                    game_state.game_over = True
                    break

        else:
            for ghost in ghosts:
                start: tuple[int, int] = (
                    ghost.y,
                    ghost.x,
                )

                if start == position_player:
                    game_state.game_over = True
                    break

                ### Athos
                if ghost.name == "Athos":
                    road: list[tuple[int, int]] = bfs(
                        start,
                        position_player,
                        maze,
                    )

                    if len(road) > 1:
                        ghost.move_to_position(road[1])

                # ### Porthos
                elif ghost.name == "Porthos":
                    target: tuple[int, int] = preshoot(
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

                # ### Dartagnan
                elif ghost.name == "Dartagnan":
                    next_pos = unpredictable(
                        start,
                        position_player,
                        maze,
                    )

                    ghost.move_to_position(next_pos)

                # Aramis
                else:
                    path: dict[str, int] | None = (
                        ghost.check_path(maze)
                    )

                    if path is not None:
                        direction: str | None = move_randomly(
                            path,
                            last_paths[ghost.name],
                        )

                        if direction is not None:
                            ghost.move_to_direction(direction)
                            last_paths[ghost.name] = direction

                if (ghost.y, ghost.x) == position_player:
                    game_state.game_over = True
                    break

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

    list_pacgum: dict[tuple[int, int], bool] = {}
    list_super_pacgum: dict[tuple[int, int], bool] = {}
    game_state = GameState(
        score=0,
        position_pacgum=list_pacgum,
        position_super_pacgum=list_super_pacgum,
        level=1,
        remaining_time=config.level_max_time,
        frightened=False,
        game_over=False,
        victory=False,
        cheat=False,
    )

    level_index: int = game_state.level - 1
    level: LevelConfig = config.levels[level_index]

    generator = MazeGenerator(
        size=(level.width, level.height),
        perfect=config.perfect,
        seed=config.seed,
    )

    maze: list[list[int]] = generator.maze

    game_state.position_pacgum = generate_pacgum(maze, config.pacgum)
    game_state.position_super_pacgum = generate_super_pacgum(maze)

    player_x: int
    player_y: int
    player_x, player_y = find_player_spawn(maze)

    player = Player(
        x=player_x,
        y=player_y,
        spawn_position=(player_x, player_y),
        direction=(1, 0),
        lives=config.lives,
    )

    height: int = len(maze) - 1
    width: int = len(maze[0]) - 1

    ghosts: list[Ghost] = [
        Ghost(0, 0, (0, 0), "Athos"),
        Ghost(width, 0, (width, 0), "Porthos"),
        Ghost(0, height, (0, height), "Aramis"),
        Ghost(width, height, (width, height),
              "Dartagnan"),
    ]

    return maze, player, ghosts, game_state
