from mazegenerator import MazeGenerator
from src.maze import game
import curses

def main() -> None:
    """Start the terminal Pac-Man test."""
    curses.wrapper(game)



if __name__ == "__main__":
    main()
