"""Load graphical resources and share display dimensions."""

from pathlib import Path

import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Pac-Man"
UI_SCALE = 1.0
HUD_HEIGHT = 86
TILE_SIZE = 24
PACMAN_SIZE = (30, 30)
PACMAN_SEQUENCE = (0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 0)

HUD_BACKGROUND_COLOR = (15, 22, 58)
WALL_COLOR = (42, 112, 255)

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


GHOST_IMAGES: dict[str, dict[str, pygame.Surface]] = {}
PACGUM_IMAGE: pygame.Surface = pygame.Surface((1, 1))
Super_PACGUM_IMAGE: pygame.Surface = pygame.Surface((1, 1))
HUD_IMAGE: pygame.Surface = pygame.Surface((1, 1))
BACKGROUND_IMAGE: pygame.Surface = pygame.Surface((1, 1))

ASSETS_FOLDER: Path = Path(__file__).resolve().parents[2] / "assets"
PACMAN_FOLDER: Path = ASSETS_FOLDER / "geometric" / "pacman"
FONT_FOLDER: Path = ASSETS_FOLDER / "font"
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
    global HUD_HEIGHT, TILE_SIZE, PACMAN_SIZE, PACGUM_IMAGE, Super_PACGUM_IMAGE
    global HUD_IMAGE, BACKGROUND_IMAGE
    screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
    window_size = (
        int(screen_width * 0.85), int(screen_height * 0.85)
    )

    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption(WINDOW_TITLE)
    WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
    UI_SCALE = min(WINDOW_WIDTH / 800, WINDOW_HEIGHT / 600)
    HUD_HEIGHT = scaled(86)
    TILE_SIZE = scaled(24)
    PACMAN_SIZE = (scaled(30), scaled(30))
    HUD_IMAGE = create_hud_image()
    BACKGROUND_IMAGE = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    fonts = load_fonts()

    path = PACMAN_FOLDER.parent / "pellets" / "pacgum.png"
    image = pygame.image.load(path)
    PACGUM_IMAGE = resize_image(image, (scaled(12), scaled(12)))
    path = PACMAN_FOLDER.parent / "pellets" / "super_pacgum.png"
    image = pygame.image.load(path)
    Super_PACGUM_IMAGE = resize_image(image, (scaled(18), scaled(18)))
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
        )
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


def load_pacman_images() -> PacmanImages:
    """Load the eight prepared frames for each direction once at startup."""
    images: PacmanImages = {}
    for direction in ("left", "right", "up", "down"):
        images[direction] = []
        for number in range(8):
            path = PACMAN_FOLDER / direction / f"frame_{number:02d}.png"
            image = pygame.image.load(path)
            images[direction].append(resize_image(image, PACMAN_SIZE))
    return images


def load_ghost_images() -> None:
    """Load normal, frightened, and returning ghost textures."""
    for name in ("Athos", "Porthos", "Aramis", "Dartagnan"):
        folder = PACMAN_FOLDER.parent / "ghosts" / name.lower()
        GHOST_IMAGES[name] = {}
        for state in ("normal", "frightened", "returning"):
            image = pygame.image.load(folder / f"{state}.png")
            GHOST_IMAGES[name][state] = resize_image(
                image, (TILE_SIZE, TILE_SIZE)
            )


def create_hud_image() -> pygame.Surface:
    """Prepare the HUD background once at its final size."""
    image = pygame.Surface((WINDOW_WIDTH, HUD_HEIGHT))
    for y in range(HUD_HEIGHT):
        for x in range(WINDOW_WIDTH):
            image.set_at((x, y), HUD_BACKGROUND_COLOR)
    return image
