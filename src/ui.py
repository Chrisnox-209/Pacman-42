"""Pygame drawing and interface helpers for Pac-Man."""

from pathlib import Path
from typing import Callable, Literal

import curses
import pygame

from src.parse import ParseConfig, ParseHighScore
from src.game import GameState, Player
from src.ghost import Ghost
from src.interface import create_game


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Pac-Man"
UI_SCALE = 1.0
HUD_HEIGHT = 86
TILE_SIZE = 24
PACMAN_SIZE = (30, 30)
PACMAN_SEQUENCE = (0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 0)

BACKGROUND_COLOR = (8, 12, 38)
HUD_BACKGROUND_COLOR = (15, 22, 58)
WALL_COLOR = (42, 112, 255)

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

MENU_OPTIONS = ("Start Game", "Highscores", "Instructions", "Quit")

GHOST_IMAGES: dict[str, dict[str, pygame.Surface]] = {}
PACGUM_IMAGE: pygame.Surface
HUD_IMAGE: pygame.Surface

PACMAN_FOLDER: Path = (
    Path(__file__).parent.parent / "assets" / "geometric" / "pacman"
)

FONT_FOLDER = Path(__file__).parent.parent / "assets" / "font"
TITLE_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ -?"
TEXT_CHARACTERS = "".join(chr(code) for code in range(32, 127))
FONT_COLUMNS = 16
FONT_WIDTH = 20
FONT_HEIGHT = 24

BitmapFont = dict[str, pygame.Surface]
FontSet = dict[str, BitmapFont]
PacmanImages = dict[str, list[pygame.Surface]]


def scaled(value: int) -> int:
    """Convert a reference size to pixels for the current window."""
    return max(1, round(value * UI_SCALE))


def create_display() -> tuple[pygame.Surface, FontSet, PacmanImages]:
    """Create the window and prepare graphics at their final size."""
    global WINDOW_WIDTH, WINDOW_HEIGHT, UI_SCALE
    global HUD_HEIGHT, TILE_SIZE, PACMAN_SIZE, PACGUM_IMAGE
    global HUD_IMAGE
    screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
    window_size: tuple[int, int] = (int(screen_width * 0.85), int(screen_height * 0.85))

    pygame.key.set_repeat(180, 100)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption(WINDOW_TITLE)
    WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
    UI_SCALE = min(WINDOW_WIDTH / 800, WINDOW_HEIGHT / 600)
    HUD_HEIGHT = scaled(86)
    TILE_SIZE = scaled(24)
    PACMAN_SIZE = (scaled(30), scaled(30))
    HUD_IMAGE = create_hud_image()

    fonts = load_fonts()

    path = PACMAN_FOLDER.parent / "pellets" / "pacgum.png"
    image = pygame.image.load(path).convert_alpha()
    PACGUM_IMAGE = resize_image(image, (scaled(12), scaled(12)))
    load_ghost_images()
    return screen, fonts, load_pacman_images()


def resize_image(
    image: pygame.Surface,
    size: tuple[int, int],
) -> pygame.Surface:
    """Resize an image by copying the nearest source pixel, including alpha."""
    original_width, original_height = image.get_size()
    new_width, new_height = size
    resized = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(new_height):
        source_y = y * original_height // new_height
        for x in range(new_width):
            source_x = x * original_width // new_width
            resized.set_at((x, y), image.get_at((source_x, source_y)))
    return resized


def load_fonts() -> FontSet:
    """Load both atlases and extract their characters once at startup."""
    fonts: FontSet = {}
    for style, characters in (
        ("title", TITLE_CHARACTERS),
        ("text", TEXT_CHARACTERS),
    ):
        atlas = pygame.image.load(
            FONT_FOLDER / f"{style}.png"
        ).convert_alpha()
        fonts[style] = {}
        for index, character in enumerate(characters):
            letter = pygame.Surface(
                (FONT_WIDTH, FONT_HEIGHT), pygame.SRCALPHA
            )
            source_x = (index % FONT_COLUMNS) * FONT_WIDTH
            source_y = (index // FONT_COLUMNS) * FONT_HEIGHT
            for y in range(FONT_HEIGHT):
                for x in range(FONT_WIDTH):
                    letter.set_at(
                        (x, y),
                        atlas.get_at((source_x + x, source_y + y)),
                    )
            fonts[style][character] = resize_image(
                letter, (scaled(FONT_WIDTH), scaled(FONT_HEIGHT))
            )
    return fonts


def render_text(font: BitmapFont, text: str) -> pygame.Surface:
    """Build a text image using the loaded characters."""
    width, height = font[" "].get_size()
    spacing = scaled(14)
    image = pygame.Surface(
        (max(1, (len(text) - 1) * spacing + width), height),
        pygame.SRCALPHA,
    )
    for index, character in enumerate(text):
        letter = font.get(character, font["?"])
        image.blit(letter, (index * spacing, 0))
    return image


def load_pacman_images() -> PacmanImages:
    """Load the eight prepared frames for each direction once at startup."""
    images: PacmanImages = {}
    for direction in ("left", "right", "up", "down"):
        images[direction] = []
        for number in range(8):
            path = PACMAN_FOLDER / direction / f"frame_{number:02d}.png"
            image = pygame.image.load(path).convert_alpha()
            images[direction].append(resize_image(image, PACMAN_SIZE))
    return images


def load_ghost_images() -> None:
    """Load normal and frightened ghost textures once at startup."""
    for name in ("Athos", "Porthos", "Aramis", "Dartagnan"):
        folder = PACMAN_FOLDER.parent / "ghosts" / name.lower()
        GHOST_IMAGES[name] = {}
        for state in ("normal", "frightened"):
            image = pygame.image.load(folder / f"{state}.png").convert_alpha()
            GHOST_IMAGES[name][state] = resize_image(
                image, (TILE_SIZE, TILE_SIZE)
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


def draw_wall(
    screen: pygame.Surface,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    """Draw a wall rectangle one pixel at a time."""
    for pixel_y in range(y, y + height):
        for pixel_x in range(x, x + width):
            screen.set_at((pixel_x, pixel_y), WALL_COLOR)


def draw_maze_grid(
    screen: pygame.Surface,
    maze: list[list[int]],
    maze_origin: tuple[int, int],
    position_pacgum: dict[tuple[int, int], bool],
    position_super_pacgum: dict[tuple[int, int], bool],
) -> None:
    """Draw walls pixel by pixel and open cells as pellets."""
    origin_x, origin_y = maze_origin
    thickness: int = scaled(1)

    for y, row in enumerate(maze):
        for x, walls in enumerate(row):
            left: int = origin_x + x * TILE_SIZE
            top: int = origin_y + y * TILE_SIZE
            right: int = left + TILE_SIZE
            bottom: int = top + TILE_SIZE

            if walls & NORTH:
                draw_wall(screen, left, top, TILE_SIZE, thickness)
            if walls & EAST:
                draw_wall(
                    screen, right - thickness, top, thickness, TILE_SIZE
                )
            if walls & SOUTH:
                draw_wall(
                    screen, left, bottom - thickness, TILE_SIZE, thickness
                )
            if walls & WEST:
                draw_wall(screen, left, top, thickness, TILE_SIZE)

            for key, value in position_pacgum.items():
                if (y, x) == key and value:
                    rect: pygame.Rect = PACGUM_IMAGE.get_rect(center=cell_center(x, y, maze_origin))
                    screen.blit(PACGUM_IMAGE, rect)

            for key, value in position_super_pacgum.items():
                if (y, x) == key and value:
                    # ### Desiner les superpacgum ici
                    pass


def create_hud_image() -> pygame.Surface:
    """Prepare the HUD background once at its final size."""
    image = pygame.Surface((WINDOW_WIDTH, HUD_HEIGHT))
    for y in range(HUD_HEIGHT):
        for x in range(WINDOW_WIDTH):
            image.set_at((x, y), HUD_BACKGROUND_COLOR)
    return image


def draw_hud(
    screen: pygame.Surface,
    fonts: FontSet,
    game_state: GameState,
    player: Player,
) -> None:
    """Display the current score, lives, level, and remaining time."""
    screen.blit(HUD_IMAGE, (0, 0))
    pygame.draw.line(
        screen,
        WALL_COLOR,
        (0, HUD_HEIGHT - 1),
        (WINDOW_WIDTH, HUD_HEIGHT - 1),
        scaled(2),
    )

    stats: tuple[tuple[str, str, int], tuple[str, str, int],
                 tuple[str, str, int], tuple[str, str, int]] = (
        ("SCORE", f"{game_state.score:06d}", 28),
        ("LIVES", str(player.lives), 230),
        ("LEVEL", str(game_state.level), 425),
        ("TIME", f"{game_state.remaining_time}s", 620),
    )

    for label, value, x in stats:
        screen.blit(
            render_text(fonts["text"], label),
            (WINDOW_WIDTH * x // 800, scaled(15)),
        )
        screen.blit(
            render_text(fonts["text"], value),
            (WINDOW_WIDTH * x // 800, scaled(42)),
        )


def get_player_facing(direction: tuple[int, int]) -> str:
    """Convert the player's (dx, dy) direction to a sprite-facing name."""
    directions: dict[tuple[int, int], str] = {
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
    animation_frame: int,
) -> None:
    """Draw the player sprite at its current maze cell."""
    facing: str = get_player_facing(player.direction)
    image: pygame.Surface = images[facing][animation_frame]
    image_rect: pygame.Rect = image.get_rect(
        center=cell_center(player.x, player.y, maze_origin)
    )
    screen.blit(image, image_rect)


def draw_ghosts(
    screen: pygame.Surface,
    ghosts: list[Ghost],
    maze_origin: tuple[int, int],
    frightened: bool,
) -> None:
    """Draw the ghost texture matching the current frightened mode."""
    state: Literal['frightened'] | Literal['normal'] = "frightened" if frightened else "normal"
    for ghost in ghosts:
        image: pygame.Surface = GHOST_IMAGES[ghost.name][state]
        rect: pygame.Rect = image.get_rect(
            center=cell_center(ghost.x, ghost.y, maze_origin)
        )
        screen.blit(image, rect)


def draw_game(
    screen: pygame.Surface,
    fonts: FontSet,
    images: PacmanImages,
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
    animation_frame: int,
) -> None:
    """Draw the HUD, maze, player, and ghosts for one frame."""
    maze_origin: tuple[int, int] = get_maze_origin(maze)
    draw_hud(screen, fonts, game_state, player)
    draw_maze_grid(screen, maze, maze_origin,
                   game_state.position_pacgum,
                   game_state.position_super_pacgum,)
    draw_player(screen, images, player, maze_origin, animation_frame)
    draw_ghosts(screen, ghosts, maze_origin, game_state.frightened)


def draw_menu(
    screen: pygame.Surface,
    fonts: FontSet,
    selected_option: int,
) -> None:
    """Draw the main menu and highlight the selected option."""
    title = render_text(fonts["title"], "PAC-MAN")
    screen.blit(
        title,
        title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)),
    )

    for index, option in enumerate(MENU_OPTIONS):
        selected = index == selected_option
        prefix = ">  " if selected else "   "
        image = render_text(fonts["text"], prefix + option)
        screen.blit(
            image,
            image.get_rect(
                center=(
                    WINDOW_WIDTH // 2,
                    WINDOW_HEIGHT * (270 + index * 55) // 600,
                )
            ),
        )

    help_text = render_text(
        fonts["text"], "UP / DOWN: select     ENTER: choose"
    )
    screen.blit(
        help_text,
        help_text.get_rect(center=(WINDOW_WIDTH // 2,
                                   WINDOW_HEIGHT * 530 // 600)),
    )


def draw_message(
    screen: pygame.Surface,
    fonts: FontSet,
    title: str,
    lines: tuple[str, ...],
) -> None:
    """Draw an information, pause, or game-over screen."""
    title_image = render_text(fonts["title"], title.upper())
    screen.blit(
        title_image,
        title_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)),
    )

    for index, line in enumerate(lines):
        line_image = render_text(fonts["text"], line)
        screen.blit(
            line_image,
            line_image.get_rect(
                center=(
                    WINDOW_WIDTH // 2,
                    WINDOW_HEIGHT * (270 + index * 48) // 600,
                )
            ),
        )

    footer = render_text(fonts["text"], "ENTER or ESC: return")
    screen.blit(
        footer,
        footer.get_rect(center=(WINDOW_WIDTH // 2,
                                WINDOW_HEIGHT * 530 // 600)),
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
    animation_frame: int,
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
            animation_frame,
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
    elif current_screen == "game_over":
        draw_message(
            screen,
            fonts,
            "GAME OVER",
            (f"Final score: {game_state.score}",),
        )


class GameWindow:
    """Provide the input method expected by the original game loop."""

    def __init__(self) -> None:
        self.screen, self.fonts, self.images = create_display()
        self.closed = False
        self.animation_frame = 0
        self.pending_key = -1
        self.last_player_position: tuple[int, int] | None = None

    def refresh(self) -> None:
        """Display the frame directly, without resizing it."""
        pygame.display.flip()

    def getch(self) -> int:
        """Translate Pygame input into the original terminal key codes."""
        arrow_keys = {
            pygame.K_UP: curses.KEY_UP,
            pygame.K_RIGHT: curses.KEY_RIGHT,
            pygame.K_DOWN: curses.KEY_DOWN,
            pygame.K_LEFT: curses.KEY_LEFT,
        }

        key = self.pending_key
        self.pending_key = -1

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
            self.refresh()

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
    """Animate the display during the 300 ms between game updates."""
    position: tuple[int, int] = (player.x, player.y)
    moving: bool = (
        window.last_player_position is not None
        and position != window.last_player_position
    )
    window.last_player_position = position
    clock = pygame.time.Clock()
    start: int = pygame.time.get_ticks()

    while not window.closed:
        window.pending_key = window.getch()
        elapsed: int = pygame.time.get_ticks() - start
        if window.closed or elapsed >= 300:
            break

        window.animation_frame = (PACMAN_SEQUENCE[elapsed // 20]
                                  if moving else 0)
        window.screen.fill(BACKGROUND_COLOR)
        draw_game(
            window.screen,
            window.fonts,
            window.images,
            maze,
            player,
            ghosts,
            game_state,
            window.animation_frame,
        )
        window.refresh()
        clock.tick(60)


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
    config: ParseConfig,
    scores: ParseHighScore
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
                    if current_screen == "game_over" and event.key in (
                        pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE
                    ):
                        maze, player, ghosts, game_state = create_game(config)
                        window.last_player_position = None
                        window.animation_frame = 0
                        window.pending_key = -1
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
                    config,
                )
                if window.closed:
                    break
                current_screen = "game_over"
                continue

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
                window.animation_frame,
            )
            window.refresh()
            clock.tick(60)

    finally:
        pygame.quit()
