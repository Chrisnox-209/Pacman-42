"""Prototype d'écran Pac-Man avec labyrinthe de test et HUD."""

from pathlib import Path

import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Pac-Man"
BACKGROUND_COLOR = (8, 12, 38)
HUD_BACKGROUND_COLOR = (15, 22, 58)
HUD_LABEL_COLOR = (153, 174, 255)
HUD_VALUE_COLOR = (255, 255, 255)
MAZE_WALL_COLOR = (42, 112, 255)
PELLET_COLOR = (255, 224, 170)
PACMAN_SIZE = (24, 24)
MAZE_TILE_SIZE = 28
HUD_HEIGHT = 86
WALL_THICKNESS = 3
PACMAN_IMAGE_PATH = Path(__file__).parent / "assets" / "pacman.png"
PACMAN_CLOSED_IMAGE_PATH = (
    Path(__file__).parent / "assets" / "pacman_closed.png"
)
PACMAN_SPEED = 180
ANIMATION_INTERVAL = 0.15
ROTATION_ANGLES = {"left": 0, "down": 90, "right": 180, "up": 270}

NORTH_WALL = 1
EAST_WALL = 2
SOUTH_WALL = 4
WEST_WALL = 8

TEST_MAZE_LAYOUT = (
    "###############",
    "#.............#",
    "#.###.###.###.#",
    "#.#...#...#...#",
    "#.#.###.#.###.#",
    "#.#.....#.....#",
    "#.#####.#####.#",
    "#.............#",
    "#.###.###.###.#",
    "#...#.....#...#",
    "###.#.###.#.###",
    "#.............#",
    "###############",
)
MazeGrid = list[list[int]]


def build_test_maze(layout: tuple[str, ...]) -> MazeGrid:
    """Convertit un plan de test en masques de murs comme le générateur."""
    maze: MazeGrid = []
    height = len(layout)
    width = len(layout[0])

    for row_index, row in enumerate(layout):
        maze_row: list[int] = []
        for column_index, tile in enumerate(row):
            if tile == "#":
                maze_row.append(15)
                continue

            walls = 0
            if row_index == 0 or layout[row_index - 1][column_index] == "#":
                walls |= NORTH_WALL
            if column_index == width - 1 or row[column_index + 1] == "#":
                walls |= EAST_WALL
            if row_index == height - 1 or layout[row_index + 1][column_index] == "#":
                walls |= SOUTH_WALL
            if column_index == 0 or row[column_index - 1] == "#":
                walls |= WEST_WALL
            maze_row.append(walls)
        maze.append(maze_row)

    return maze


def get_maze_origin(maze: MazeGrid) -> tuple[int, int]:
    """Centre le labyrinthe dans l'espace situé sous le HUD."""
    maze_width = len(maze[0]) * MAZE_TILE_SIZE
    maze_height = len(maze) * MAZE_TILE_SIZE
    x = (WINDOW_WIDTH - maze_width) // 2
    available_height = WINDOW_HEIGHT - HUD_HEIGHT
    y = HUD_HEIGHT + (available_height - maze_height) // 2
    return x, y


def draw_maze(
    screen: pygame.Surface,
    maze: MazeGrid,
    origin: tuple[int, int],
) -> None:
    """Dessine les murs et les pac-gommes du labyrinthe."""
    origin_x, origin_y = origin
    for row_index, row in enumerate(maze):
        for column_index, walls in enumerate(row):
            x = origin_x + column_index * MAZE_TILE_SIZE
            y = origin_y + row_index * MAZE_TILE_SIZE
            tile_rect = pygame.Rect(x, y, MAZE_TILE_SIZE, MAZE_TILE_SIZE)

            if walls == 15:
                pygame.draw.rect(screen, MAZE_WALL_COLOR, tile_rect)
                continue

            if walls & NORTH_WALL:
                pygame.draw.line(
                    screen, MAZE_WALL_COLOR, (x, y),
                    (x + MAZE_TILE_SIZE, y), WALL_THICKNESS
                )
            if walls & EAST_WALL:
                pygame.draw.line(
                    screen, MAZE_WALL_COLOR,
                    (x + MAZE_TILE_SIZE, y),
                    (x + MAZE_TILE_SIZE, y + MAZE_TILE_SIZE),
                    WALL_THICKNESS
                )
            if walls & SOUTH_WALL:
                pygame.draw.line(
                    screen, MAZE_WALL_COLOR,
                    (x, y + MAZE_TILE_SIZE),
                    (x + MAZE_TILE_SIZE, y + MAZE_TILE_SIZE),
                    WALL_THICKNESS
                )
            if walls & WEST_WALL:
                pygame.draw.line(
                    screen, MAZE_WALL_COLOR, (x, y),
                    (x, y + MAZE_TILE_SIZE), WALL_THICKNESS
                )

            pellet_position = tile_rect.center
            pygame.draw.circle(screen, PELLET_COLOR, pellet_position, 2)


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
        screen, MAZE_WALL_COLOR,
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


def move_pacman(
    position: tuple[float, float],
    direction: tuple[int, int],
    delta_time: float,
    bounds: pygame.Rect,
) -> tuple[float, float]:
    """Déplace Pac-Man et le garde dans les limites du labyrinthe."""
    x, y = position
    dx, dy = direction
    half_width = PACMAN_SIZE[0] / 2
    half_height = PACMAN_SIZE[1] / 2
    x += dx * PACMAN_SPEED * delta_time
    y += dy * PACMAN_SPEED * delta_time
    x = max(bounds.left + half_width, min(bounds.right - half_width, x))
    y = max(bounds.top + half_height, min(bounds.bottom - half_height, y))
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
    label_font = pygame.font.Font(None, 24)
    value_font = pygame.font.Font(None, 34)
    open_image = pygame.image.load(PACMAN_IMAGE_PATH).convert_alpha()
    open_image = pygame.transform.smoothscale(open_image, PACMAN_SIZE)
    closed_image = pygame.image.load(
        PACMAN_CLOSED_IMAGE_PATH
    ).convert_alpha()
    closed_image = pygame.transform.smoothscale(closed_image, PACMAN_SIZE)
    test_maze = build_test_maze(TEST_MAZE_LAYOUT)
    maze_origin = get_maze_origin(test_maze)
    maze_bounds = pygame.Rect(
        maze_origin,
        (len(test_maze[0]) * MAZE_TILE_SIZE,
         len(test_maze) * MAZE_TILE_SIZE),
    )
    pacman_position = (float(maze_bounds.centerx), float(maze_bounds.centery))
    score = 0
    lives = 3
    level = 1
    remaining_time = 90
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
                pacman_position, move_direction, delta_time, maze_bounds
            )
            animation_time += delta_time
            if animation_time >= ANIMATION_INTERVAL:
                mouth_open = not mouth_open
                animation_time = 0.0
        else:
            mouth_open = True
            animation_time = 0.0

        draw_hud(
            screen, label_font, value_font, score, lives, level,
            remaining_time
        )
        draw_maze(screen, test_maze, maze_origin)
        draw_pacman(
            screen, open_image, closed_image, pacman_position,
            direction, mouth_open
        )
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
