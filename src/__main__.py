"""Start the Pac-Man application."""

from src.game import create_game, run
from src.ui import wrapper


def main() -> None:
    """Prepare the game and launch the graphical interface."""
    maze, player, ghosts, game_state = create_game()
    wrapper(run, maze, player, ghosts, game_state)


if __name__ == "__main__":
    main()
