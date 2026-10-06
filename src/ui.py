"""Pygame drawing and interface helpers for Pac-Man."""

from pathlib import Path
from typing import Callable

import curses
import pygame

from src.game import GameState, Player
from src.ghost import Ghost


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Pac-Man"
HUD_HEIGHT = 86
TILE_SIZE = 24
PACMAN_SIZE = (20, 20)

BACKGROUND_COLOR = (8, 12, 38)
HUD_BACKGROUND_COLOR = (15, 22, 58)
HUD_LABEL_COLOR = (153, 174, 255)
HUD_VALUE_COLOR = (255, 255, 255)
MENU_TEXT_COLOR = (220, 225, 255)
MENU_SELECTED_COLOR = (255, 224, 70)
WALL_COLOR = (42, 112, 255)
PELLET_COLOR = (255, 224, 170)

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

MENU_OPTIONS = ("Start Game", "Highscores", "Instructions", "Quit")

GHOST_COLORS: dict[str, tuple[int, int, int]] = {
    "Athos": (255, 70, 70),
    "Porthos": (255, 145, 210),
    "Aramis": (80, 230, 255),
    "Dartagnan": (255, 170, 50),
}

PACMAN_IMAGE = Path(__file__).parent.parent / "assets" / "pacman.png"
PACMAN_CLOSED_IMAGE = (
    Path(__file__).parent.parent / "assets" / "pacman_closed.png"
)

ROTATION_ANGLES = {"left": 0, "down": 90, "right": 180, "up": 270}
FontSet = dict[str, pygame.font.Font]
PacmanImages = tuple[pygame.Surface, pygame.Surface]


def create_display() -> tuple[pygame.Surface, FontSet, PacmanImages]:
    """Create the window and load the fonts and Pac-Man images."""
    pygame.key.set_repeat(180, 100)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    fonts: FontSet = {
        "title": pygame.font.Font(None, 72),
        "menu": pygame.font.Font(None, 34),
        "info": pygame.font.Font(None, 30),
        "hud_label": pygame.font.Font(None, 24),
        "hud_value": pygame.font.Font(None, 34),
    }
    return screen, fonts, load_pacman_images()


def load_pacman_images() -> PacmanImages:
    """Load and resize the open- and closed-mouth Pac-Man images."""
    open_image = pygame.image.load(PACMAN_IMAGE).convert_alpha()
    closed_image = pygame.image.load(PACMAN_CLOSED_IMAGE).convert_alpha()
    return (
        pygame.transform.smoothscale(open_image, PACMAN_SIZE),
        pygame.transform.smoothscale(closed_image, PACMAN_SIZE),
    )


def handle_key(
    key: int,
    current_screen: str,
    selected_option: int,
) -> tuple[bool, str, int]:
    """Handle menu navigation and screen changes for one key press."""
    if current_screen == "menu":
        if key == pygame.K_UP:
            selected_option = (selected_option - 1) % len(MENU_OPTIONS)
        elif key == pygame.K_DOWN:
            selected_option = (selected_option + 1) % len(MENU_OPTIONS)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if selected_option == 0:
                current_screen = "game"
            elif selected_option == 1:
                current_screen = "highscores"
            elif selected_option == 2:
                current_screen = "instructions"
            else:
                return False, current_screen, selected_option

    elif current_screen == "game" and key == pygame.K_ESCAPE:
        current_screen = "paused"

    elif current_screen == "paused":
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            current_screen = "game"
        elif key == pygame.K_ESCAPE:
            current_screen = "menu"

    elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
        current_screen = "menu"

    return True, current_screen, selected_option


def get_maze_origin(maze: list[list[int]]) -> tuple[int, int]:
    """Center the maze in the game area below the HUD."""
    maze_width = len(maze[0]) * TILE_SIZE
    maze_height = len(maze) * TILE_SIZE
    x = (WINDOW_WIDTH - maze_width) // 2
    available_height = WINDOW_HEIGHT - HUD_HEIGHT
    y = HUD_HEIGHT + (available_height - maze_height) // 2
    return x, y


def cell_center(
    x: int,
    y: int,
    maze_origin: tuple[int, int],
) -> tuple[int, int]:
    """Convert a maze cell coordinate into its pixel center."""
    origin_x, origin_y = maze_origin
    return (
        origin_x + x * TILE_SIZE + TILE_SIZE // 2,
        origin_y + y * TILE_SIZE + TILE_SIZE // 2,
    )


def draw_maze_grid(
    screen: pygame.Surface,
    maze: list[list[int]],
    maze_origin: tuple[int, int],
) -> None:
    """Draw the wall bits as blue lines and open cells as pellets."""
    origin_x, origin_y = maze_origin

    for y, row in enumerate(maze):
        for x, walls in enumerate(row):
            left = origin_x + x * TILE_SIZE
            top = origin_y + y * TILE_SIZE
            right = left + TILE_SIZE
            bottom = top + TILE_SIZE

            if walls & NORTH:
                pygame.draw.line(
                    screen, WALL_COLOR, (left, top), (right, top), 3
                )
            if walls & EAST:
                pygame.draw.line(
                    screen, WALL_COLOR, (right, top), (right, bottom), 3
                )
            if walls & SOUTH:
                pygame.draw.line(
                    screen, WALL_COLOR, (left, bottom), (right, bottom), 3
                )
            if walls & WEST:
                pygame.draw.line(
                    screen, WALL_COLOR, (left, top), (left, bottom), 3
                )

            if walls != 15:
                pygame.draw.circle(
                    screen,
                    PELLET_COLOR,
                    cell_center(x, y, maze_origin),
                    2,
                )


def draw_hud(
    screen: pygame.Surface,
    fonts: FontSet,
    game_state: GameState,
    player: Player,
) -> None:
    """Display the current score, lives, level, and remaining time."""
    pygame.draw.rect(
        screen,
        HUD_BACKGROUND_COLOR,
        (0, 0, WINDOW_WIDTH, HUD_HEIGHT),
    )
    pygame.draw.line(
        screen,
        WALL_COLOR,
        (0, HUD_HEIGHT - 1),
        (WINDOW_WIDTH, HUD_HEIGHT - 1),
        2,
    )

    stats = (
        ("SCORE", f"{game_state.score:06d}", 28),
        ("LIVES", str(player.lives), 230),
        ("LEVEL", str(game_state.level), 425),
        ("TIME", f"{game_state.remaining_time}s", 620),
    )

    for label, value, x in stats:
        screen.blit(
            fonts["hud_label"].render(label, True, HUD_LABEL_COLOR),
            (x, 15),
        )
        screen.blit(
            fonts["hud_value"].render(value, True, HUD_VALUE_COLOR),
            (x, 42),
        )


def get_player_facing(direction: tuple[int, int]) -> str:
    """Convert the player's (dx, dy) direction to a sprite-facing name."""
    directions = {
        (-1, 0): "left",
        (0, 1): "down",
        (1, 0): "right",
        (0, -1): "up",
    }
    return directions.get(direction, "right")


def draw_player(
    screen: pygame.Surface,
    images: PacmanImages,
    player: Player,
    maze_origin: tuple[int, int],
    mouth_open: bool,
) -> None:
    """Draw the player sprite at its current maze cell."""
    image = images[0] if mouth_open else images[1]
    facing = get_player_facing(player.direction)
    rotated_image = pygame.transform.rotate(
        image,
        ROTATION_ANGLES[facing],
    )
    image_rect = rotated_image.get_rect(
        center=cell_center(player.x, player.y, maze_origin)
    )
    screen.blit(rotated_image, image_rect)


def draw_ghosts(
    screen: pygame.Surface,
    ghosts: list[Ghost],
    maze_origin: tuple[int, int],
) -> None:
    """Draw all ghosts at their current maze cells."""
    for ghost in ghosts:
        color = GHOST_COLORS.get(
            ghost.name,
            (255, 255, 255),
        )
        pygame.draw.circle(
            screen,
            color,
            cell_center(ghost.x, ghost.y, maze_origin),
            8,
        )


def draw_game(
    screen: pygame.Surface,
    fonts: FontSet,
    images: PacmanImages,
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
    mouth_open: bool,
) -> None:
    """Draw the HUD, maze, player, and ghosts for one frame."""
    maze_origin = get_maze_origin(maze)
    draw_hud(screen, fonts, game_state, player)
    draw_maze_grid(screen, maze, maze_origin)
    draw_player(screen, images, player, maze_origin, mouth_open)
    draw_ghosts(screen, ghosts, maze_origin)


def draw_menu(
    screen: pygame.Surface,
    fonts: FontSet,
    selected_option: int,
) -> None:
    """Draw the main menu and highlight the selected option."""
    title = fonts["title"].render(
        "PAC-MAN",
        True,
        MENU_SELECTED_COLOR,
    )
    screen.blit(
        title,
        title.get_rect(center=(WINDOW_WIDTH // 2, 150)),
    )

    for index, option in enumerate(MENU_OPTIONS):
        selected = index == selected_option
        color = MENU_SELECTED_COLOR if selected else MENU_TEXT_COLOR
        prefix = ">  " if selected else "   "
        image = fonts["menu"].render(prefix + option, True, color)
        screen.blit(
            image,
            image.get_rect(
                center=(WINDOW_WIDTH // 2, 270 + index * 55)
            ),
        )

    help_text = fonts["menu"].render(
        "UP / DOWN: select     ENTER: choose",
        True,
        HUD_LABEL_COLOR,
    )
    screen.blit(
        help_text,
        help_text.get_rect(center=(WINDOW_WIDTH // 2, 530)),
    )


def draw_message(
    screen: pygame.Surface,
    fonts: FontSet,
    title: str,
    lines: tuple[str, ...],
) -> None:
    """Draw an information, pause, or game-over screen."""
    title_image = fonts["title"].render(
        title,
        True,
        MENU_SELECTED_COLOR,
    )
    screen.blit(
        title_image,
        title_image.get_rect(center=(WINDOW_WIDTH // 2, 150)),
    )

    for index, line in enumerate(lines):
        line_image = fonts["info"].render(
            line,
            True,
            MENU_TEXT_COLOR,
        )
        screen.blit(
            line_image,
            line_image.get_rect(
                center=(WINDOW_WIDTH // 2, 270 + index * 48)
            ),
        )

    footer = fonts["info"].render(
        "ENTER or ESC: return",
        True,
        HUD_LABEL_COLOR,
    )
    screen.blit(
        footer,
        footer.get_rect(center=(WINDOW_WIDTH // 2, 530)),
    )


def draw_screen(
    screen: pygame.Surface,
    current_screen: str,
    selected_option: int,
    fonts: FontSet,
    images: PacmanImages,
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
    mouth_open: bool,
) -> None:
    """Clear the window and draw the active screen."""
    screen.fill(BACKGROUND_COLOR)

    if current_screen == "menu":
        draw_menu(screen, fonts, selected_option)
    elif current_screen == "game":
        draw_game(
            screen,
            fonts,
            images,
            maze,
            player,
            ghosts,
            game_state,
            mouth_open,
        )
    elif current_screen == "instructions":
        draw_message(
            screen,
            fonts,
            "INSTRUCTIONS",
            (
                "Use arrow keys or WASD to move.",
                "Press ESC to pause the game.",
            ),
        )
    elif current_screen == "highscores":
        draw_message(
            screen,
            fonts,
            "HIGHSCORES",
            ("No scores saved yet.",),
        )
    elif current_screen == "paused":
        draw_message(
            screen,
            fonts,
            "PAUSED",
            ("ENTER: resume", "ESC: return to menu"),
        )
    else:
        draw_message(
            screen,
            fonts,
            "GAME OVER",
            ("Press ENTER to return to the menu.",),
        )


class GameWindow:
    """Provide the input method expected by the original game loop."""

    def __init__(self) -> None:
        self.screen, self.fonts, self.images = create_display()
        self.closed = False
        self.mouth_open = True
        self.last_player_position: tuple[int, int] | None = None

    def getch(self) -> int:
        """Translate Pygame input into the original terminal key codes."""
        arrow_keys = {
            pygame.K_UP: curses.KEY_UP,
            pygame.K_RIGHT: curses.KEY_RIGHT,
            pygame.K_DOWN: curses.KEY_DOWN,
            pygame.K_LEFT: curses.KEY_LEFT,
        }

        key = -1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.closed = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.closed = True
                elif event.key == pygame.K_ESCAPE:
                    self.pause()
                elif event.key in arrow_keys:
                    key = arrow_keys[event.key]
                elif event.unicode:
                    key = ord(event.unicode[0])

        return ord("q") if self.closed else key

    def pause(self) -> None:
        """Wait for the user to resume without updating game objects."""
        clock = pygame.time.Clock()

        while not self.closed:
            self.screen.fill(BACKGROUND_COLOR)
            draw_message(
                self.screen,
                self.fonts,
                "PAUSED",
                ("ENTER or ESC: resume", "Q: quit"),
            )
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.closed = True
                elif event.type == pygame.KEYDOWN:
                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER,
                        pygame.K_ESCAPE,
                    ):
                        return
                    if event.key == pygame.K_q:
                        self.closed = True

            clock.tick(60)


def setup_terminal(window: GameWindow) -> None:
    """Prepare the graphical display using the original hook name."""
    window.screen.fill(BACKGROUND_COLOR)


def draw_maze(
    window: GameWindow,
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
) -> None:
    """Display the game with the signature used by the main run loop."""
    position = (player.x, player.y)

    if (
        window.last_player_position is not None
        and position != window.last_player_position
    ):
        window.mouth_open = not window.mouth_open

    window.last_player_position = position
    window.screen.fill(BACKGROUND_COLOR)

    draw_game(
        window.screen,
        window.fonts,
        window.images,
        maze,
        player,
        ghosts,
        game_state,
        window.mouth_open,
    )
    pygame.display.flip()


def wrapper(
    run: Callable[
        [
            GameWindow,
            list[list[int]],
            Player,
            list[Ghost],
            GameState,
        ],
        None,
    ],
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
) -> None:
    """Show the menu, then call the game loop with Pygame I/O."""
    pygame.init()

    try:
        window = GameWindow()
        clock = pygame.time.Clock()
        current_screen = "menu"
        selected_option = 0
        running = True

        while running and not window.closed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    window.closed = True
                elif event.type == pygame.KEYDOWN:
                    running, current_screen, selected_option = handle_key(
                        event.key,
                        current_screen,
                        selected_option,
                    )

            if not running or window.closed:
                break

            if current_screen == "game":
                run(
                    window,
                    maze,
                    player,
                    ghosts,
                    game_state,
                )
                break

            draw_screen(
                window.screen,
                current_screen,
                selected_option,
                window.fonts,
                window.images,
                maze,
                player,
                ghosts,
                game_state,
                window.mouth_open,
            )
            pygame.display.flip()
            clock.tick(60)

    finally:
        pygame.quit()
