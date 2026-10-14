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

    last_player_move: float = time.monotonic()
    last_ghost_move: float = time.monotonic()
    last_time: float = time.monotonic()

    player_delay: float = 1 / config.speed_player
    ghost_delay: float = 1 / config.speed_ghosts

    frightened_start_time: float | None = None
    movement_key: int = -1

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

    level_index: int = game_state.level - 1
    level: LevelConfig = config.levels[level_index]

    def verifier_collision(ghost: Ghost) -> bool:
        if (ghost.y, ghost.x) != (player.y, player.x):
            return False

        if ghost.state == "frightened":
            ghost.state = "dead"
            game_state.score += config.points_per_ghost
            return False

        if ghost.state == "normal":
            game_state.game_over = True
            return True

        return False

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

        if current_time - last_player_move >= player_delay:
            move_player(
                maze,
                player,
                movement_key,
            )
            last_player_move = current_time

        position_player: tuple[int, int] = (
            player.y,
            player.x,
        )

        if game_state.position_super_pacgum.get(
            position_player,
            False,
        ):
            game_state.position_super_pacgum[
                position_player
            ] = False

            game_state.score += (
                config.points_per_super_pacgum
            )

            game_state.frightened = True
            frightened_start_time = current_time

            for ghost in ghosts:
                if ghost.state == "normal":
                    ghost.state = "frightened"

        if game_state.position_pacgum.get(
            position_player,
            False,
        ):
            game_state.position_pacgum[
                position_player
            ] = False

            game_state.score += config.points_per_pacgum

        if (
            game_state.frightened
            and frightened_start_time is not None
        ):
            time_escape: float = (
                current_time - frightened_start_time
            )

            if time_escape >= level.escape_time:
                game_state.frightened = False
                frightened_start_time = None

                for ghost in ghosts:
                    if ghost.state == "frightened":
                        ghost.state = "normal"

        for ghost in ghosts:
            if verifier_collision(ghost):
                return

        if (
            not any(game_state.position_pacgum.values())
            and not any(
                game_state.position_super_pacgum.values()
            )
        ):
            game_state.level += 1
            game_state.victory = True
            return

        if current_time - last_ghost_move >= ghost_delay:
            for ghost in ghosts:
                start: tuple[int, int] = (
                    ghost.y,
                    ghost.x,
                )

                if ghost.state == "dead":
                    spawn: tuple[int, int] = (
                        ghost.spawn_position[1],
                        ghost.spawn_position[0],
                    )

                    road: list[tuple[int, int]] = bfs(
                        start,
                        spawn,
                        maze,
                    )

                    if len(road) > 1:
                        ghost.move_to_position(road[1])

                    if (ghost.y, ghost.x) == spawn:
                        last_positions[ghost.name] = None

                        if game_state.frightened:
                            ghost.state = "frightened"
                        else:
                            ghost.state = "normal"

                    continue

                if ghost.state == "frightened":
                    next_pos: tuple[int, int] = to_flee(
                        start,
                        position_player,
                        last_positions[ghost.name],
                        maze,
                    )

                    last_positions[ghost.name] = start
                    ghost.move_to_position(next_pos)

                elif ghost.state == "normal":
                    if ghost.name == "Athos":
                        road = bfs(
                            start,
                            position_player,
                            maze,
                        )

                        if len(road) > 1:
                            ghost.move_to_position(road[1])

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

                    elif ghost.name == "Dartagnan":
                        next_pos = unpredictable(
                            start,
                            position_player,
                            maze,
                        )

                        ghost.move_to_position(next_pos)

                    elif ghost.name == "Aramis":
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

                if verifier_collision(ghost):
                    return

            last_ghost_move = current_time

        draw_maze(
            stdscr,
            maze,
            player,
            ghosts,
            game_state,
        )


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
        Ghost(0, 0, (0, 0), "Athos", "normal"),
        Ghost(width, 0, (width, 0), "Porthos", "normal"),
        Ghost(0, height, (0, height), "Aramis", "normal"),
        Ghost(width, height, (width, height),
              "Dartagnan", "normal"),
    ]

    return maze, player, ghosts, game_state
