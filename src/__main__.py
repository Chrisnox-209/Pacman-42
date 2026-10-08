from src.game import create_game, run
from src.ui import wrapper
from src.utils import check_config, Color
from src.parse import ConfigPathError, check_argument
import sys


def main(config: str) -> None:

    try:
        check_config(config)
    except ConfigPathError as error:
        print(f"{Color.RED.value}[ERROR]{Color.RST.value} {error}")
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
