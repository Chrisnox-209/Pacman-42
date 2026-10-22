"""Draw text, the maze, characters, and the HUD."""

import pygame

from src.models.game import GameState, Player
from src.models.ghost import Ghost
from . import resources
from .resources import BitmapFont, FontSet, PacmanImages, scaled


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


def draw_centered(
    screen: pygame.Surface,
    image: pygame.Surface,
    center: tuple[int, int],
) -> None:
    """Draw an image with its center at the given coordinates."""
    width, height = image.get_size()
    x = center[0] - width // 2
    y = center[1] - height // 2
    screen.blit(image, (x, y))


def get_maze_origin(maze: list[list[int]]) -> tuple[int, int]:
    """Center the maze in the game area below the HUD."""
    maze_width = len(maze[0]) * resources.TILE_SIZE
    maze_height = len(maze) * resources.TILE_SIZE
    x = (resources.WINDOW_WIDTH - maze_width) // 2
    available_height = resources.WINDOW_HEIGHT - resources.HUD_HEIGHT
    y = resources.HUD_HEIGHT + (available_height - maze_height) // 2
    return x, y


def cell_center(
    x: int,
    y: int,
    maze_origin: tuple[int, int],
) -> tuple[int, int]:
    """Convert a maze cell coordinate into its pixel center."""
    origin_x, origin_y = maze_origin
    return (
        origin_x + x * resources.TILE_SIZE + resources.TILE_SIZE // 2,
        origin_y + y * resources.TILE_SIZE + resources.TILE_SIZE // 2,
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
            screen.set_at((pixel_x, pixel_y), resources.WALL_COLOR)


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
            left: int = origin_x + x * resources.TILE_SIZE
            top: int = origin_y + y * resources.TILE_SIZE
            right: int = left + resources.TILE_SIZE
            bottom: int = top + resources.TILE_SIZE

            if walls & resources.NORTH:
                draw_wall(screen, left, top, resources.TILE_SIZE, thickness)
            if walls & resources.EAST:
                draw_wall(
                    screen, right - thickness, top,
                    thickness, resources.TILE_SIZE
                )
            if walls & resources.SOUTH:
                draw_wall(
                    screen, left, bottom - thickness,
                    resources.TILE_SIZE, thickness
                )
            if walls & resources.WEST:
                draw_wall(screen, left, top, thickness, resources.TILE_SIZE)

            if position_pacgum.get((y, x), False):
                draw_centered(
                    screen, resources.PACGUM_IMAGE,
                    cell_center(x, y, maze_origin),
                )

            if position_super_pacgum.get((y, x), False):
                draw_centered(
                    screen, resources.Super_PACGUM_IMAGE,
                    cell_center(x, y, maze_origin),
                )


def draw_hud(
    screen: pygame.Surface,
    fonts: FontSet,
    game_state: GameState,
    player: Player,
) -> None:
    """Display the current score, lives, level, and remaining time."""
    screen.blit(resources.HUD_IMAGE, (0, 0))
    draw_wall(
        screen,
        0,
        resources.HUD_HEIGHT - scaled(2),
        resources.WINDOW_WIDTH,
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
            (resources.WINDOW_WIDTH * x // 800, scaled(15)),
        )
        screen.blit(
            render_text(fonts["text"], value),
            (resources.WINDOW_WIDTH * x // 800, scaled(42)),
        )


def draw_cheat_menu(
    screen: pygame.Surface,
    fonts: FontSet,
    noclip: bool,
    invincible: bool,
    next_level_requested: bool,
) -> None:
    """Display cheat controls and their interface states."""
    screen.blit(resources.HUD_IMAGE, (0, 0))

    title = render_text(fonts["title"], "CHEATS")
    screen.blit(title, (scaled(28), scaled(15)))

    noclip_status = "ON" if noclip else "OFF"
    invincible_status = "ON" if invincible else "OFF"
    level_status = "OK" if next_level_requested else "-"

    text = (
        f"N:No clip {noclip_status}  "
        f"L:Next {level_status}  "
        f"I:Invincible {invincible_status}"
    )

    image = render_text(fonts["text"], text)
    screen.blit(image, (scaled(28), scaled(42)))


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
    draw_centered(
        screen, image,
        cell_center(player.x, player.y, maze_origin),
    )


def draw_ghosts(
    screen: pygame.Surface,
    ghosts: list[Ghost],
    maze_origin: tuple[int, int],
    frightened: bool,
) -> None:
    """Draw normal, frightened, or returning ghost textures."""
    for ghost in ghosts:
        if ghost.state == "dead":
            state = "returning"

        elif ghost.state == "frightened":
            state = "frightened"
        else:
            state = "normal"

        image: pygame.Surface = resources.GHOST_IMAGES[
            ghost.name
        ][state]

        draw_centered(
            screen, image,
            cell_center(ghost.x, ghost.y, maze_origin),
        )


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
