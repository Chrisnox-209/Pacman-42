from typing import TYPE_CHECKING
import curses
import time

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


def check_collision(ghost: Ghost, player: Player,
                    game_state: GameState, config: ParseConfig, ) -> bool:
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


def update_pacgums_and_frightened(player: Player, ghosts: list[Ghost],
                                  game_state: GameState, config: ParseConfig,
                                  level: LevelConfig, current_time: float,
                                  frightened_start_time: float | None,
                                  ) -> float | None:
    position_player: tuple[int, int] = (player.y, player.x)

    if position_player in game_state.position_super_pacgum:
        if game_state.position_super_pacgum[position_player] is True:
            game_state.position_super_pacgum[position_player] = False
            game_state.score += config.points_per_super_pacgum
            game_state.frightened = True
            frightened_start_time = current_time

            for ghost in ghosts:
                if ghost.state == "normal":
                    ghost.state = "frightened"

    if position_player in game_state.position_pacgum:
        if game_state.position_pacgum[position_player] is True:
            game_state.position_pacgum[position_player] = False
            game_state.score += config.points_per_pacgum

    if game_state.frightened and frightened_start_time is not None:
        time_escape: float = current_time - frightened_start_time

        if time_escape >= level.escape_time:
            game_state.frightened = False
            frightened_start_time = None

            for ghost in ghosts:
                if ghost.state == "frightened":
                    ghost.state = "normal"

    return frightened_start_time


def check_victory(game_state: GameState, ) -> bool:
    for is_present in game_state.position_pacgum.values():
        if is_present is True:
            return False

    for is_present in game_state.position_super_pacgum.values():
        if is_present is True:
            return False

    game_state.level += 1
    game_state.victory = True
    return True


def move_ghost(ghost: Ghost, player: Player, maze: list[list[int]],
               last_positions: dict[str, tuple[int, int] | None],
               last_paths: dict[str, str | None],
               ghost_respawn_time: dict[str, float | None],
               current_time: float, time_respawn: int,
               frightened: bool) -> None:

    start: tuple[int, int] = (ghost.y, ghost.x)
    position_player: tuple[int, int] = (player.y, player.x)

    if ghost.state == "dead":
        spawn: tuple[int, int] = (
            ghost.spawn_position[0],
            ghost.spawn_position[1],
        )
        road: list[tuple[int, int]] = bfs(start, spawn, maze)

        if len(road) > 1:
            ghost.move_to_position(road[1])
        elif len(road) == 1:
            ghost.move_to_position(road[0])

        if (ghost.y, ghost.x) == spawn:
            start_respawn: float | None = ghost_respawn_time[ghost.name]
            if start_respawn is None:
                ghost_respawn_time[ghost.name] = current_time
            else:
                total_time: float = current_time - start_respawn
                if total_time >= time_respawn:
                    last_positions[ghost.name] = None
                    ghost_respawn_time[ghost.name] = None

                    if frightened:
                        ghost.state = "frightened"
                    else:
                        ghost.state = "normal"

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
        if ghost.name == "Athos":
            road = bfs(start, position_player, maze)
            if len(road) > 1:
                ghost.move_to_position(road[1])

        elif ghost.name == "Porthos":
            target: tuple[int, int] = preshoot(position_player, maze)
            road = bfs(start, target, maze)
            if len(road) > 1:
                ghost.move_to_position(road[1])

        elif ghost.name == "Dartagnan":
            next_pos = unpredictable(start, position_player, maze)
            ghost.move_to_position(next_pos)

        elif ghost.name == "Aramis":
            path: dict[str, int] | None = ghost.check_path(maze)
            if path is not None:
                direction: str | None = move_randomly(
                    path,
                    last_paths[ghost.name],
                )
                if direction is not None:
                    ghost.move_to_direction(direction)
                    last_paths[ghost.name] = direction


def run(stdscr: "GameWindow", maze: list[list[int]],
        player: Player, ghosts: list[Ghost],
        game_state: GameState, config: ParseConfig, ) -> None:
    from src.ui import draw_maze, setup_terminal

    setup_terminal(stdscr)

    last_player_move: float = time.monotonic()
    last_ghost_move: float = time.monotonic()
    last_dead_move: float = time.monotonic()
    last_time: float = time.monotonic()

    player_delay: float = 1 / config.speed_player
    ghost_delay: float = 1 / config.speed_ghosts
    dead_delay: float = ghost_delay / 3

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

    ghost_respawn_time: dict[str, float | None] = {
        "Athos": None,
        "Porthos": None,
        "Aramis": None,
        "Dartagnan": None,
    }

    level_index: int = game_state.level - 1
    level: LevelConfig = config.levels[level_index]

    while not game_state.game_over:
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
            move_player(maze, player, movement_key)
            last_player_move = current_time

        frightened_start_time = update_pacgums_and_frightened(
            player,
            ghosts,
            game_state,
            config,
            level,
            current_time,
            frightened_start_time,
        )

        for ghost in ghosts:
            if check_collision(ghost, player, game_state, config):
                return

        if check_victory(game_state):
            return

        move_ghosts: bool = current_time - last_ghost_move >= ghost_delay
        move_dead: bool = current_time - last_dead_move >= dead_delay

        for ghost in ghosts:
            if ghost.state == "dead":
                if not move_dead:
                    continue
            elif not move_ghosts:
                continue

            move_ghost(ghost, player, maze, last_positions,
                       last_paths, ghost_respawn_time,
                       current_time, config.time_respawn_ghost,
                       game_state.frightened)

            if check_collision(ghost, player, game_state, config):
                return

        if move_ghosts:
            last_ghost_move = current_time

        if move_dead:
            last_dead_move = current_time

        draw_maze(stdscr, maze, player, ghosts, game_state)
