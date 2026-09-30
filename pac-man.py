"""Premier prototype : ouvrir puis fermer proprement une fenêtre Pygame."""

from pathlib import Path

import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Pac-Man"
BACKGROUND_COLOR = (8, 12, 38)
PACMAN_SIZE = (96, 96)
PACMAN_IMAGE_PATH = Path(__file__).parent / "assets" / "pacman.png"
PACMAN_CLOSED_IMAGE_PATH = (
    Path(__file__).parent / "assets" / "pacman_closed.png"
)
PACMAN_SPEED = 260
ANIMATION_INTERVAL = 0.15
ROTATION_ANGLES = {"left": 0, "down": 90, "right": 180, "up": 270}


def move_pacman(
    position: tuple[float, float],
    direction: tuple[int, int],
    delta_time: float,
) -> tuple[float, float]:
    """Déplace Pac-Man et le garde entièrement dans la fenêtre."""
    x, y = position
    dx, dy = direction
    half_width = PACMAN_SIZE[0] / 2
    half_height = PACMAN_SIZE[1] / 2
    x += dx * PACMAN_SPEED * delta_time
    y += dy * PACMAN_SPEED * delta_time
    x = max(half_width, min(WINDOW_WIDTH - half_width, x))
    y = max(half_height, min(WINDOW_HEIGHT - half_height, y))
    return x, y


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


def main() -> None:
    """Déplace Pac-Man au clavier et anime sa bouche pendant le mouvement."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    open_image = pygame.image.load(PACMAN_IMAGE_PATH).convert_alpha()
    open_image = pygame.transform.smoothscale(open_image, PACMAN_SIZE)
    closed_image = pygame.image.load(
        PACMAN_CLOSED_IMAGE_PATH
    ).convert_alpha()
    closed_image = pygame.transform.smoothscale(closed_image, PACMAN_SIZE)
    pacman_position = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
    direction = "right"
    mouth_open = True
    animation_time = 0.0
    clock = pygame.time.Clock()

    running = True
    while running:
        delta_time = clock.tick(60) / 1000

        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        movement = {
            pygame.K_RIGHT: ("right", (1, 0)),
            pygame.K_LEFT: ("left", (-1, 0)),
            pygame.K_UP: ("up", (0, -1)),
            pygame.K_DOWN: ("down", (0, 1)),
        }
        move_direction = (0, 0)
        for key, (new_direction, vector) in movement.items():
            if keys[key]:
                direction = new_direction
                move_direction = vector
                break

        if move_direction != (0, 0):
            pacman_position = move_pacman(
                pacman_position, move_direction, delta_time
            )
            animation_time += delta_time
            if animation_time >= ANIMATION_INTERVAL:
                mouth_open = not mouth_open
                animation_time = 0.0
        else:
            mouth_open = True
            animation_time = 0.0

        draw_pacman(
            screen, open_image, closed_image, pacman_position,
            direction, mouth_open
        )
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
