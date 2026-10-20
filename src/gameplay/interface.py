"""Create levels and move the player through the maze."""


from mazegenerator import MazeGenerator

from src.models.ghost import Ghost
from src.models.game import Player, GameState
from src.config.parse import ParseConfig, LevelConfig
from src.common.utils import (generate_pacgum,
                              find_player_spawn,
                              generate_super_pacgum)

from typing import Any
import curses


def move_player(
    maze: list[list[int]],
    player: Player,
    key: int,
    noclip: bool = False,
) -> None:
    """Move one cell for the key while respecting bounds and noclip."""
    wall: int = maze[player.y][player.x]

    if key in (curses.KEY_UP, ord("w")):
        if player.y > 0 and (noclip or wall & 1 == 0):
            player.y -= 1
            player.direction = (0, -1)

    elif key in (curses.KEY_RIGHT, ord("d")):
        if (
            player.x < len(maze[player.y]) - 1
            and (noclip or wall & 2 == 0)
        ):
            player.x += 1
            player.direction = (1, 0)

    elif key in (curses.KEY_DOWN, ord("s")):
        if (
            player.y < len(maze) - 1
            and (noclip or wall & 4 == 0)
        ):
            player.y += 1
            player.direction = (0, 1)

    elif key in (curses.KEY_LEFT, ord("a")):
        if player.x > 0 and (noclip or wall & 8 == 0):
            player.x -= 1
            player.direction = (-1, 0)


def create_game(config: ParseConfig, level_number: int = 1,
                score: int = 0, lives: int | None = None
                ) -> tuple[list[list[int]], Player, list[Ghost], GameState]:
    """Build a level with the supplied score and remaining lives.

    Use a fixed seed only for level one and (row, column) spawn positions.
    Raise ValueError when the requested level is outside the configuration.
    """
    list_pacgum: dict[tuple[int, int], bool] = {}
    list_super_pacgum: dict[tuple[int, int], bool] = {}
    game_state = GameState(
        score=score,
        position_pacgum=list_pacgum,
        position_super_pacgum=list_super_pacgum,
        level=level_number,
        remaining_time=config.level_max_time,
        frightened=False,
        game_over=False,
        victory=False,
        cheat=False,
    )

    if not 1 <= level_number <= len(config.levels):
        raise ValueError("Invalid level number")

    level_index: int = game_state.level - 1
    level: LevelConfig = config.levels[level_index]

    if game_state.level == 1:
        generator: Any = MazeGenerator(
            size=(level.width, level.height),
            perfect=config.perfect,
            seed=config.seed,
        )
    else:
        generator = MazeGenerator(
            size=(level.width, level.height),
            perfect=config.perfect,
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
        spawn_position=(player_y, player_x),
        direction=(1, 0),
        lives=config.lives if lives is None else lives,
    )

    height: int = len(maze) - 1
    width: int = len(maze[0]) - 1

    ghosts: list[Ghost] = [
        Ghost(0, 0, (0, 0), "Athos", "normal"),
        Ghost(width, 0, (0, width), "Porthos", "normal"),
        Ghost(0, height, (height, 0), "Aramis", "normal"),
        Ghost(width, height, (height, width),
              "Dartagnan", "normal"),
    ]

    return maze, player, ghosts, game_state
