"""Prototype Pygame avec menu principal, Pac-Man et HUD."""

from pathlib import Path

import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Pac-Man"
BACKGROUND_COLOR = (8, 12, 38)
HUD_BACKGROUND_COLOR = (15, 22, 58)
HUD_LABEL_COLOR = (153, 174, 255)
HUD_VALUE_COLOR = (255, 255, 255)
MENU_TEXT_COLOR = (220, 225, 255)
MENU_SELECTED_COLOR = (255, 224, 70)
HUD_LINE_COLOR = (42, 112, 255)
PACMAN_SIZE = (24, 24)
HUD_HEIGHT = 86
PACMAN_IMAGE_PATH = Path(__file__).parent / "assets" / "pacman.png"
PACMAN_CLOSED_IMAGE_PATH = (
    Path(__file__).parent / "assets" / "pacman_closed.png"
)
PACMAN_SPEED = 180
ANIMATION_INTERVAL = 0.15
ROTATION_ANGLES = {"left": 0, "down": 90, "right": 180, "up": 270}

MENU_OPTIONS = ("Start Game", "Highscores", "Instructions", "Quit")


def draw_hud(
    screen: pygame.Surface,
    label_font: pygame.font.Font,
    value_font: pygame.font.Font,
    score: int,
    lives: int,
    level: int,
    remaining_time: int,
) -> None:
    """Affiche le score, les vies, le niveau et le temps restant."""
    pygame.draw.rect(
        screen, HUD_BACKGROUND_COLOR,
        (0, 0, WINDOW_WIDTH, HUD_HEIGHT)
    )
    pygame.draw.line(
        screen, HUD_LINE_COLOR,
        (0, HUD_HEIGHT - 1), (WINDOW_WIDTH, HUD_HEIGHT - 1), 2
    )

    stats = (
        ("SCORE", f"{score:06d}", 28),
        ("LIVES", str(lives), 230),
        ("LEVEL", str(level), 425),
        ("TIME", f"{remaining_time}s", 620),
    )
    for label, value, x in stats:
        label_image = label_font.render(label, True, HUD_LABEL_COLOR)
        value_image = value_font.render(value, True, HUD_VALUE_COLOR)
        screen.blit(label_image, (x, 15))
        screen.blit(value_image, (x, 42))


def draw_menu(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    option_font: pygame.font.Font,
    selected_option: int,
) -> None:
    """Affiche le titre du jeu et les choix du menu principal."""
    title = title_font.render("PAC-MAN", True, MENU_SELECTED_COLOR)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
    screen.blit(title, title_rect)

    for index, option in enumerate(MENU_OPTIONS):
        is_selected = index == selected_option
        color = MENU_SELECTED_COLOR if is_selected else MENU_TEXT_COLOR
        prefix = ">  " if is_selected else "   "
        option_image = option_font.render(prefix + option, True, color)
        option_rect = option_image.get_rect(
            center=(WINDOW_WIDTH // 2, 270 + index * 55)
        )
        screen.blit(option_image, option_rect)

    help_text = option_font.render(
        "UP / DOWN: select     ENTER: choose", True, HUD_LABEL_COLOR
    )
    help_rect = help_text.get_rect(center=(WINDOW_WIDTH // 2, 530))
    screen.blit(help_text, help_rect)


def draw_info_page(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    text_font: pygame.font.Font,
    title: str,
    lines: tuple[str, ...],
) -> None:
    """Affiche une page simple avec un titre, du texte et le retour."""
    title_image = title_font.render(title, True, MENU_SELECTED_COLOR)
    title_rect = title_image.get_rect(center=(WINDOW_WIDTH // 2, 150))
    screen.blit(title_image, title_rect)

    for index, line in enumerate(lines):
        line_image = text_font.render(line, True, MENU_TEXT_COLOR)
        line_rect = line_image.get_rect(
            center=(WINDOW_WIDTH // 2, 270 + index * 48)
        )
        screen.blit(line_image, line_rect)

    return_image = text_font.render(
        "ENTER or ESC: return to menu", True, HUD_LABEL_COLOR
    )
    return_rect = return_image.get_rect(center=(WINDOW_WIDTH // 2, 530))
    screen.blit(return_image, return_rect)


def move_pacman(
    position: tuple[float, float],
    direction: tuple[int, int],
    delta_time: float,
    bounds: pygame.Rect,
) -> tuple[float, float]:
    """Déplace Pac-Man et le garde dans la zone de jeu."""
    x, y = position
    dx, dy = direction
    half_width = PACMAN_SIZE[0] / 2
    half_height = PACMAN_SIZE[1] / 2
    x += dx * PACMAN_SPEED * delta_time
    y += dy * PACMAN_SPEED * delta_time
    x = max(bounds.left + half_width, min(bounds.right - half_width, x))
    y = max(bounds.top + half_height, min(bounds.bottom - half_height, y))
    return x, y


def load_pacman_images() -> tuple[pygame.Surface, pygame.Surface]:
    """Charge et redimensionne les images de Pac-Man."""
    open_image = pygame.image.load(PACMAN_IMAGE_PATH).convert_alpha()
    closed_image = pygame.image.load(PACMAN_CLOSED_IMAGE_PATH).convert_alpha()
    return (
        pygame.transform.smoothscale(open_image, PACMAN_SIZE),
        pygame.transform.smoothscale(closed_image, PACMAN_SIZE),
    )


def handle_event(
    event: pygame.event.Event,
    current_screen: str,
    selected_option: int,
) -> tuple[bool, str, int]:
    """Met à jour l'écran ou la sélection selon un événement clavier."""
    if event.type == pygame.QUIT:
        return False, current_screen, selected_option

    if event.type != pygame.KEYDOWN:
        return True, current_screen, selected_option

    if current_screen == "menu":
        if event.key == pygame.K_UP:
            selected_option = (selected_option - 1) % len(MENU_OPTIONS)
        elif event.key == pygame.K_DOWN:
            selected_option = (selected_option + 1) % len(MENU_OPTIONS)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if selected_option == 0:
                current_screen = "game"
            elif selected_option == 1:
                current_screen = "highscores"
            elif selected_option == 2:
                current_screen = "instructions"
            else:
                return False, current_screen, selected_option
    elif current_screen in ("highscores", "instructions"):
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
            current_screen = "menu"
    elif current_screen == "game" and event.key == pygame.K_ESCAPE:
        current_screen = "menu"

    return True, current_screen, selected_option


def read_movement(
    keys: pygame.key.ScancodeWrapper,
) -> tuple[str, tuple[int, int]] | None:
    """Renvoie la direction associée à la flèche maintenue."""
    movement = (
        (pygame.K_RIGHT, "right", (1, 0)),
        (pygame.K_LEFT, "left", (-1, 0)),
        (pygame.K_UP, "up", (0, -1)),
        (pygame.K_DOWN, "down", (0, 1)),
    )
    for key, direction, vector in movement:
        if keys[key]:
            return direction, vector
    return None


def update_pacman(
    keys: pygame.key.ScancodeWrapper,
    delta_time: float,
    position: tuple[float, float],
    direction: str,
    mouth_open: bool,
    animation_time: float,
    game_bounds: pygame.Rect,
) -> tuple[tuple[float, float], str, bool, float]:
    """Déplace Pac-Man et alterne ses images quand il avance."""
    movement = read_movement(keys)
    if movement is None:
        return position, direction, True, 0.0

    direction, move_vector = movement
    position = move_pacman(position, move_vector, delta_time, game_bounds)
    animation_time += delta_time
    if animation_time >= ANIMATION_INTERVAL:
        mouth_open = not mouth_open
        animation_time = 0.0
    return position, direction, mouth_open, animation_time


def draw_pacman(
    screen: pygame.Surface,
    open_image: pygame.Surface,
    closed_image: pygame.Surface,
    position: tuple[float, float],
    direction: str,
    mouth_open: bool,
) -> None:
    """Dessine Pac-Man orienté dans la direction choisie."""
    image = open_image if mouth_open else closed_image
    rotated_image = pygame.transform.rotate(
        image, ROTATION_ANGLES[direction]
    )
    image_rect = rotated_image.get_rect(
        center=(round(position[0]), round(position[1]))
    )
    screen.blit(rotated_image, image_rect)


def draw_game_screen(
    screen: pygame.Surface,
    label_font: pygame.font.Font,
    value_font: pygame.font.Font,
    open_image: pygame.Surface,
    closed_image: pygame.Surface,
    score: int,
    lives: int,
    level: int,
    remaining_time: int,
    position: tuple[float, float],
    direction: str,
    mouth_open: bool,
) -> None:
    """Dessine l'écran de jeu vide avec son HUD et Pac-Man."""
    draw_hud(screen, label_font, value_font, score, lives, level, remaining_time)
    draw_pacman(screen, open_image, closed_image, position, direction, mouth_open)


def draw_current_screen(
    screen: pygame.Surface,
    current_screen: str,
    selected_option: int,
    fonts: tuple[pygame.font.Font, ...],
    images: tuple[pygame.Surface, pygame.Surface],
    game_data: tuple[int, int, int, int, tuple[float, float], str, bool],
) -> None:
    """Choisit le dessin à afficher selon l'écran courant."""
    title_font, menu_font, info_font, label_font, value_font = fonts
    open_image, closed_image = images

    if current_screen == "menu":
        draw_menu(screen, title_font, menu_font, selected_option)
    elif current_screen == "highscores":
        draw_info_page(
            screen, title_font, info_font, "HIGHSCORES",
            ("No scores saved yet.",),
        )
    elif current_screen == "instructions":
        draw_info_page(
            screen, title_font, info_font, "INSTRUCTIONS",
            ("Use the arrow keys to move Pac-Man.",
             "Press ESC to return to the menu."),
        )
    else:
        score, lives, level, remaining_time, position, direction, mouth_open = game_data
        draw_game_screen(
            screen, label_font, value_font, open_image, closed_image,
            score, lives, level, remaining_time, position, direction, mouth_open,
        )


def main() -> None:
    """Initialise le jeu puis orchestre ses mises à jour et son affichage."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    fonts = (
        pygame.font.Font(None, 72),
        pygame.font.Font(None, 34),
        pygame.font.Font(None, 30),
        pygame.font.Font(None, 24),
        pygame.font.Font(None, 34),
    )
    images = load_pacman_images()
    game_bounds = pygame.Rect(
        0, HUD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT
    )
    pacman_position = (float(WINDOW_WIDTH // 2), float(game_bounds.centery))
    score = 0
    lives = 3
    level = 1
    remaining_time = 90
    direction = "right"
    mouth_open = True
    animation_time = 0.0
    clock = pygame.time.Clock()
    current_screen = "menu"
    selected_option = 0

    running = True
    while running:
        delta_time = clock.tick(60) / 1000
        for event in pygame.event.get():
            running, current_screen, selected_option = handle_event(
                event, current_screen, selected_option
            )

        screen.fill(BACKGROUND_COLOR)
        if current_screen == "game":
            pacman_position, direction, mouth_open, animation_time = update_pacman(
                pygame.key.get_pressed(), delta_time, pacman_position,
                direction, mouth_open, animation_time, game_bounds,
            )
        game_data = (
            score, lives, level, remaining_time,
            pacman_position, direction, mouth_open,
        )
        draw_current_screen(
            screen, current_screen, selected_option, fonts, images, game_data
        )
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
