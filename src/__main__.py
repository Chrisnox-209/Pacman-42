from src.game import GameState, Player
from src.ui import GameWindow, draw_maze, setup_terminal, wrapper
from mazegenerator import MazeGenerator
import curses
import time


def find_player_spawn(
    maze: list[list[int]],
) -> tuple[int, int]:
    height: int = len(maze)
    width: int = len(maze[0])

    center_x: int = width // 2
    center_y: int = height // 2

    for radius in range(max(width, height)):
        for y in range(
            max(0, center_y - radius),
            min(height, center_y + radius + 1),
        ):
            for x in range(
                max(0, center_x - radius),
                min(width, center_x + radius + 1),
            ):
                if maze[y][x] != 15:
                    return x, y

    raise ValueError("No valid player spawn found.")


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


def run(
    stdscr: GameWindow,
    maze: list[list[int]],
    player: Player,
    game_state: GameState,
) -> None:
    setup_terminal(stdscr)

    while True:
        key: int = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            break

        move_player(
            maze,
            player,
            key,
        )

        draw_maze(
            stdscr,
            maze,
            player,
            game_state,
        )

        time.sleep(0.3)


def main() -> None:
    generator = MazeGenerator(
        size=(20, 20),
        perfect=False,
        seed=42,
    )

    maze: list[list[int]] = generator.maze
    player_x: int
    player_y: int
    player_x, player_y = find_player_spawn(maze)

    player = Player(
        x=player_x,
        y=player_y,
        spawn_position=(player_x, player_y),
        direction=(1, 0),
        lives=3,
    )

    game_state = GameState(
        score=0,
        level=1,
        remaining_time=90,
        frightened=False,
        game_over=False,
        cheat=False,
    )

    wrapper(
        run,
        maze,
        player,
        game_state,
    )


if __name__ == "__main__":
    main()
