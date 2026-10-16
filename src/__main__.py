from pathlib import Path

from src.gameplay.run import run
from src.gameplay.interface import create_game
from src.models.game import Player, GameState
from src.models.ghost import Ghost
from src.ui.ui import wrapper
from src.common.utils import Color
from src.config.parse import (ParseConfig,
                              ParseHighScore,
                              json_to_data,
                              highscore_to_data)

from pydantic import ValidationError
import sys


def main(file_config: str | None) -> None:
    maze: list[list[int]]
    player: Player
    ghosts: list[Ghost]
    game_state: GameState

    try:
        if file_config is None:
            config: ParseConfig = ParseConfig()
        else:
            config = json_to_data(file_config)
    except ValidationError as error:
        print(f"\n{Color.RED.value}[ERROR CONFIG]"
              f"{Color.ORANGE.value}",
              error.errors()[0]["msg"],
              f"{Color.RST.value}\n")
        sys.exit(1)

    except ValueError as error:
        print(f"{Color.RED.value}[ERROR CONFIG]"
              f"{Color.RST.value}", error,)
        sys.exit(1)

    try:
        file_score: Path = config.highscore_filename
        if getattr(sys, "frozen", False) and not file_score.is_absolute():
            file_score = Path.home() / ".pacman-42" / file_score
        file_score.parent.mkdir(parents=True, exist_ok=True)
        scores: ParseHighScore = highscore_to_data(file_score)
    except ValidationError as error:
        print(f"\n{Color.RED.value}[ERROR FILE SCORE]"
              f"{Color.ORANGE.value}",
              error.errors()[0]["msg"],
              f"{Color.RST.value}\n")

    except ValueError as error:
        print(f"{Color.RED.value}[ERROR FILE SCORE]"
              f"{Color.RST.value}", error,)

    maze, player, ghosts, game_state = create_game(config)

    wrapper(run, maze, player, ghosts,
            game_state, config, scores)


def cli() -> None:
    if getattr(sys, "frozen", False) and len(sys.argv) == 1:
        file_config: str | None = None

    elif len(sys.argv) == 2:
        file_config = sys.argv[1]

    else:
        print("ERROR: Configuration argument is missing or invalid.")
        sys.exit(1)
    try:
        main(file_config)

    except KeyboardInterrupt:
        print(f"\n{Color.ORANGE.value}The program was abruptly "
              f"exited by the user.{Color.RST.value}")

    except Exception as e:
        print(f"\n{Color.RED.value}[CRITICAL ERROR]{Color.RST.value} {e}",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
