from src.maze import game
from src.ghost import Ghost
from mazegenerator import MazeGenerator
import curses


def main() -> None:
    generator = MazeGenerator(
        size=(20, 20),
        perfect=False,
        seed=42,
    )

    maze = generator.maze

    ghosts = [
        Ghost(0, 0, (0, 0), "Athos"),
        Ghost(19, 0, (19, 0), "Porthos"),
        Ghost(0, 19, (0, 19), "Aramis"),
        Ghost(19, 19, (19, 19), "Dartagnan"),
    ]

    print(ghosts[0].check_path(maze))


if __name__ == "__main__":
    main()