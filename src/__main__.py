from pathlib import Path

from src.game import create_game, run, Player, GameState
from src.ghost import Ghost
from pydantic import ValidationError
from src.ui import wrapper
from src.utils import Color
from src.parse import (ParseConfig,
                       ParseHighScore,
                       json_to_data,
                       highscore_to_data)
import sys


def main(file_config: str) -> None:
    maze: list[list[int]]
    player: Player
    ghosts: list[Ghost]
    game_state: GameState

    try:
        config: ParseConfig = json_to_data(file_config)
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
        scores: ParseHighScore = highscore_to_data(file_score)
    except ValidationError as error:
        print(f"\n{Color.RED.value}[ERROR FILE SCORE]"
              f"{Color.ORANGE.value}",
              error.errors()[0]["msg"],
              f"{Color.RST.value}\n")
        sys.exit(1)

    except ValueError as error:
        print(f"{Color.RED.value}[ERROR FILE SCORE]"
              f"{Color.RST.value}", error,)
        sys.exit(1)

    maze, player, ghosts, game_state = create_game()

    wrapper(run, maze, player, ghosts, game_state)


if __name__ == "__main__":
    if len(sys.argv) > 1 and len(sys.argv) <= 2:
        file_config: str = sys.argv[1]
    else:
        print(f"\n{Color.RED.value}[ERROR] {Color.RST.value}"
              "The configuration file argument is missing.")
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
