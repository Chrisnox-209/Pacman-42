
from mazegenerator import MazeGenerator

from src.ghost import Ghost
from src.game import Player, GameState
from src.parse import ParseConfig, LevelConfig
from src.utils import (generate_pacgum,
                       find_player_spawn, generate_super_pacgum)

import curses


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
