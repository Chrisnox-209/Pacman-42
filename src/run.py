from typing import TYPE_CHECKING

from src.ghost import Ghost
from src.game import Player, GameState
from src.parse import ParseConfig, LevelConfig
from src.interface import move_player

from src.algorithm import (
    bfs,
    move_randomly,
    preshoot,
    to_flee,
    unpredictable,
)

from src.utils import time_game

if TYPE_CHECKING:
    from src.ui import GameWindow

import curses
import time


def check_collision(ghost: Ghost, player: Player,
                    game_state: GameState, config: ParseConfig) -> bool:

    if ghost.y != player.y or ghost.x != player.x:
        return False

    if ghost.state == "frightened":
        ghost.state = "dead"
        game_state.score = game_state.score + config.points_per_ghost
        return False

    if ghost.state == "normal":
        game_state.game_over = True
        return True

    return False


def check_all_collisions(ghosts: list[Ghost], player: Player,
                         game_state: GameState,
                         config: ParseConfig) -> bool:
    for ghost in ghosts:
        has_collided: bool = check_collision(ghost, player, game_state, config)
        if has_collided is not False:
            return True
    return False


def is_movement_key(key: int) -> bool:
    if key == curses.KEY_UP:
        return True
    elif key == curses.KEY_RIGHT:
        return True
    elif key == curses.KEY_DOWN:
        return True
    elif key == curses.KEY_LEFT:
        return True
    elif key == ord("w"):
        return True
    elif key == ord("d"):
        return True
    elif key == ord("s"):
        return True
    elif key == ord("a"):
        return True
    else:
        return False


def check_pacgum_eaten(player: Player, ghosts: list[Ghost],
                       game_state: GameState, config: ParseConfig,
                       current_time: float,
                       frightened_start_time: float | None) -> float | None:
    position_player: tuple[int, int] = (player.y, player.x)

    # super pacgums
    if position_player in game_state.position_super_pacgum:
        if game_state.position_super_pacgum[position_player] is not False:
            game_state.position_super_pacgum[position_player] = False
            game_state.score = (game_state.score +
                                config.points_per_super_pacgum)
            game_state.frightened = True
            frightened_start_time = current_time

            for ghost in ghosts:
                if ghost.state == "normal":
                    ghost.state = "frightened"

    # pacgums
    if position_player in game_state.position_pacgum:
        if game_state.position_pacgum[position_player] is not False:
            game_state.position_pacgum[position_player] = False
            game_state.score = game_state.score + config.points_per_pacgum

    return frightened_start_time


def update_frightened_state(ghosts: list[Ghost], game_state: GameState,
                            level: LevelConfig, current_time: float,
                            frightened_start_time: float | None
                            ) -> float | None:
    if (game_state.frightened is not False
       and frightened_start_time is not None):

        time_escape: float = current_time - frightened_start_time

        if time_escape >= level.escape_time:
            game_state.frightened = False
            frightened_start_time = None

            for ghost in ghosts:
                if ghost.state == "frightened":
                    ghost.state = "normal"

    return frightened_start_time


def check_victory(game_state: GameState) -> bool:
    for is_present in game_state.position_pacgum.values():
        if is_present is not False:
            return False

    for is_present in game_state.position_super_pacgum.values():
        if is_present is not False:
            return False

    game_state.level = game_state.level + 1
    game_state.victory = True
    return True


def move_dead_ghost(ghost: Ghost, maze: list[list[int]],
                    game_state: GameState,
                    last_positions: dict[str, tuple[int, int] | None]
                    ) -> None:
    start: tuple[int, int] = (ghost.y, ghost.x)
    spawn: tuple[int, int] = (ghost.spawn_position[0], ghost.spawn_position[1])

    road: list[tuple[int, int]] = bfs(start, spawn, maze)
    if len(road) > 1:
        ghost.move_to_position(road[1])
    elif len(road) == 1:
        ghost.move_to_position(road[0])

    if ghost.y == spawn[0] and ghost.x == spawn[1]:
        last_positions[ghost.name] = None
        ghost.state = "normal"


def move_normal_ghost(ghost: Ghost, position_player: tuple[int, int],
                      maze: list[list[int]],
                      last_paths: dict[str, str | None]) -> None:

    start: tuple[int, int] = (ghost.y, ghost.x)

    if ghost.name == "Athos":
        road: list[tuple[int, int]] = bfs(start, position_player, maze)
        if len(road) > 1:
            ghost.move_to_position(road[1])

    elif ghost.name == "Porthos":
        target: tuple[int, int] = preshoot(position_player, maze)
        road = bfs(start, target, maze)
        if len(road) > 1:
            ghost.move_to_position(road[1])

    elif ghost.name == "Dartagnan":
        next_pos: tuple[int, int] = unpredictable(start, position_player, maze)
        ghost.move_to_position(next_pos)

    elif ghost.name == "Aramis":
        path: dict[str, int] | None = ghost.check_path(maze)
        if path is not None:
            direction: str | None = move_randomly(path, last_paths[ghost.name])
            if direction is not None:
                ghost.move_to_direction(direction)
                last_paths[ghost.name] = direction


def move_single_ghost(ghost: Ghost, player: Player, maze: list[list[int]],
                      game_state: GameState,
                      last_positions: dict[str, tuple[int, int] | None],
                      last_paths: dict[str, str | None]) -> None:

    start: tuple[int, int] = (ghost.y, ghost.x)
    position_player: tuple[int, int] = (player.y, player.x)

    if ghost.state == "dead":
        move_dead_ghost(ghost, maze, game_state, last_positions)
    elif ghost.state == "frightened":
        next_pos: tuple[int, int] = to_flee(
            start,
            position_player,
            last_positions[ghost.name],
            maze,
        )
        last_positions[ghost.name] = start
        ghost.move_to_position(next_pos)
    elif ghost.state == "normal":
        move_normal_ghost(ghost, position_player, maze, last_paths)


def update_all_ghosts(ghosts: list[Ghost], player: Player,
                      maze: list[list[int]], game_state: GameState,
                      config: ParseConfig,
                      last_positions: dict[str, tuple[int, int] | None],
                      last_paths: dict[str, str | None]) -> bool:

    for ghost in ghosts:
        move_single_ghost(
            ghost,
            player,
            maze,
            game_state,
            last_positions,
            last_paths,
        )
        if check_collision(ghost, player, game_state, config) is not False:
            return True

    return False


def run(stdscr: "GameWindow", maze: list[list[int]], player: Player,
        ghosts: list[Ghost], game_state: GameState,
        config: ParseConfig) -> None:

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

    while game_state.game_over is not True:
        key: int = stdscr.getch()
        current_time: float = time.monotonic()

        if current_time - last_time >= 1:
            game_state.remaining_time = time_game(game_state.remaining_time)
            last_time = current_time

        if game_state.remaining_time == 0:
            game_state.game_over = True
            return

        if key == ord("q") or key == ord("Q"):
            return

        if is_movement_key(key) is not False:
            movement_key = key

        if current_time - last_player_move >= player_delay:
            move_player(maze, player, movement_key)
            last_player_move = current_time

        frightened_start_time = check_pacgum_eaten(
            player,
            ghosts,
            game_state,
            config,
            current_time,
            frightened_start_time,
        )

        frightened_start_time = update_frightened_state(
            ghosts,
            game_state,
            level,
            current_time,
            frightened_start_time,
        )

        if check_all_collisions(ghosts, player,
                                game_state, config) is not False:
            return

        if check_victory(game_state) is not False:
            return

        if current_time - last_ghost_move >= ghost_delay:
            ghost_killed_player: bool = update_all_ghosts(
                ghosts,
                player,
                maze,
                game_state,
                config,
                last_positions,
                last_paths,
            )
            if ghost_killed_player is not False:
                return

            last_ghost_move = current_time

        draw_maze(stdscr, maze, player, ghosts, game_state)
