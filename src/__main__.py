from src.game import create_game, run, Player, GameState
from src.ghost import Ghost
from pydantic import ValidationError
from src.ui import wrapper
from src.utils import check_config, Color
from src.parse import (ParseConfig, ConfigPathError,
                       check_argument, json_to_data)
import sys


def main(file_config: str) -> None:
    maze: list[list[int]]
    player: Player
    ghosts: list[Ghost]
    game_state: GameState

    try:
        check_config(file_config)
    except ConfigPathError as error:
        print(f"{Color.RED.value}[ERROR]{Color.RST.value} {error}")
        sys.exit(1)

    try:
        config: ParseConfig = json_to_data(file_config)
    except ValidationError as error:
        print(f"\n{Color.RED.value}[ERROR CONFIG]"
              f"{Color.ORANGE.value}",
              error.errors()[0]["msg"],
              f"{Color.RST.value}\n")
        sys.exit(1)

    maze, player, ghosts, game_state = create_game()

    wrapper(run, maze, player, ghosts, game_state)


if __name__ == "__main__":
    file_config: str

    try:
        file_config = check_argument()
        main(file_config)

    except KeyboardInterrupt:
        print(f"\n{Color.ORANGE.value}The program was abruptly "
              f"exited by the user.{Color.RST.value}")

    except Exception as e:
        print(f"\n{Color.RED.value}[CRITICAL ERROR]{Color.RST.value} {e}",
              file=sys.stderr)
        sys.exit(1)
