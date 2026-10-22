"""Draw menus and handle navigation between application screens."""

import pygame

from src.config.parse import ParseHighScore
from src.models.game import GameState, Player
from src.models.ghost import Ghost
from . import resources
from .drawing import draw_centered, draw_game, render_text
from .resources import FontSet, PacmanImages


MENU_OPTIONS = ("Start Game", "Highscores", "Instructions", "Quit")


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


def draw_menu(
    screen: pygame.Surface,
    fonts: FontSet,
    selected_option: int,
) -> None:
    """Draw the main menu and highlight the selected option."""
    title = render_text(fonts["title"], "PAC-MAN")
    draw_centered(
        screen, title,
        (resources.WINDOW_WIDTH // 2, resources.WINDOW_HEIGHT // 4),
    )

    for index, option in enumerate(MENU_OPTIONS):
        selected = index == selected_option
        prefix = ">  " if selected else "   "
        image = render_text(fonts["text"], prefix + option)
        draw_centered(
            screen, image,
            (
                resources.WINDOW_WIDTH // 2,
                resources.WINDOW_HEIGHT * (270 + index * 55) // 600,
            ),
        )

    help_text = render_text(
        fonts["text"], "UP / DOWN: select     ENTER: choose"
    )
    draw_centered(
        screen, help_text,
        (resources.WINDOW_WIDTH // 2, resources.WINDOW_HEIGHT * 530 // 600),
    )


def draw_message(
    screen: pygame.Surface,
    fonts: FontSet,
    title: str,
    lines: tuple[str, ...],
) -> None:
    """Draw an information, pause, or game-over screen."""
    title_image = render_text(fonts["title"], title.upper())
    draw_centered(
        screen, title_image,
        (resources.WINDOW_WIDTH // 2, resources.WINDOW_HEIGHT // 4),
    )

    first_y = 220 if title == "INSTRUCTIONS" else 270
    line_spacing = 38 if title == "INSTRUCTIONS" else 48
    for index, line in enumerate(lines):
        line_image = render_text(fonts["text"], line)
        draw_centered(
            screen, line_image,
            (
                resources.WINDOW_WIDTH // 2,
                resources.WINDOW_HEIGHT
                * (first_y + index * line_spacing) // 600,
            ),
        )

    if title in ("GAME OVER", "VICTORY"):
        help_text = "ENTER: confirm name"
    else:
        help_text = "ENTER or ESC: return"
    footer = render_text(fonts["text"], help_text)
    draw_centered(
        screen, footer,
        (resources.WINDOW_WIDTH // 2, resources.WINDOW_HEIGHT * 530 // 600),
    )


def draw_highscores(
    screen: pygame.Surface,
    fonts: FontSet,
    scores: ParseHighScore,
) -> None:
    """Display up to ten scores with room for every row."""
    draw_message(screen, fonts, "HIGHSCORES", ())
    ranking = sorted(
        scores.highscore, key=lambda entry: entry.score, reverse=True
    )[:10]
    lines = [
        f"{index}. {entry.name_player}: {entry.score}"
        for index, entry in enumerate(ranking, start=1)
    ] or ["No scores saved yet."]
    for index, line in enumerate(lines):
        image = render_text(fonts["text"], line)
        width, _ = image.get_size()
        screen.blit(
            image,
            ((resources.WINDOW_WIDTH - width) // 2,
             resources.WINDOW_HEIGHT * (200 + index * 28) // 600),
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
    scores: ParseHighScore,
) -> None:
    """Clear the window and draw the active screen."""
    screen.blit(resources.BACKGROUND_IMAGE, (0, 0))

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
                "Arrow keys / WASD: move",
                "ESC: pause - ENTER: resume - ESC: menu",
                "Eat all pellets and power pellets to finish a level.",
                "Power pellets let you eat ghosts for a short time.",
                "C: show or hide cheat controls",
                "N: toggle noclip - I: toggle invincibility",
                "L: skip to the next level",
                "After a win or loss: enter your name, then ENTER",
            ),
        )
    elif current_screen == "highscores":
        draw_highscores(screen, fonts, scores)
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
            "VICTORY" if game_state.victory else "GAME OVER",
            (("Congratulations!",) if game_state.victory else ())
            + (f"Final score: {game_state.score}",),
        )
