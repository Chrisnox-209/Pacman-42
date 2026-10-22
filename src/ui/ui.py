"""Connect the graphical interface to the game loop."""

from typing import Callable
import time

import pygame

from src.config.parse import ParseConfig, ParseHighScore, save_highscore
from src.models.game import GameState, Player
from src.models.ghost import Ghost
from src.gameplay.interface import create_game
from . import resources
from .drawing import draw_cheat_menu, draw_game, render_text
from .resources import scaled
from .screens import draw_screen, handle_key
from .window import GameWindow as GameWindow


def setup_terminal(window: GameWindow) -> None:
    """Prepare the graphical display using the original hook name."""
    window.screen.blit(resources.BACKGROUND_IMAGE, (0, 0))


def draw_maze(
    window: GameWindow,
    maze: list[list[int]],
    player: Player,
    ghosts: list[Ghost],
    game_state: GameState,
) -> None:
    """Draw one frame and limit rendering to approximately 60 FPS."""
    frame_start = time.perf_counter()
    now = time.monotonic()
    position = (player.x, player.y)

    if window.last_player_position is None:
        window.last_move_time = 0.0
    elif position != window.last_player_position:
        window.last_move_time = now

    window.last_player_position = position

    moving = now - window.last_move_time < 0.3
    animation_index = int(now * 1000) // 20 % len(resources.PACMAN_SEQUENCE)
    window.animation_frame = (
        resources.PACMAN_SEQUENCE[animation_index] if moving else 0
    )

    window.screen.blit(resources.BACKGROUND_IMAGE, (0, 0))
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
    if window.show_cheats:
        draw_cheat_menu(
            window.screen,
            window.fonts,
            window.noclip_enabled,
            window.invincible_enabled,
            window.next_level_requested,
        )
    window.refresh()

    frame_elapsed = time.perf_counter() - frame_start
    time.sleep(max(0, 1 / 60 - frame_elapsed))


def wrapper(
    run: Callable[
        [
            GameWindow,
            list[list[int]],
            Player,
            list[Ghost],
            GameState,
            ParseConfig,
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
        current_screen = "menu"
        selected_option = 0
        running = True

        while running and not window.closed:
            frame_start = time.perf_counter()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    window.closed = True
                elif event.type == pygame.KEYDOWN:
                    if current_screen == "game_over":
                        if event.key == pygame.K_BACKSPACE:
                            window.player_name = window.player_name[:-1]
                            continue
                        if event.key in (
                            pygame.K_RETURN, pygame.K_KP_ENTER
                        ):
                            if not window.player_name.strip():
                                continue
                            window.player_name = window.player_name.strip()
                        else:
                            character = event.unicode
                            if (
                                len(character) == 1
                                and len(window.player_name) < 10
                                and (
                                    (
                                        character.isascii()
                                        and character.isalnum()
                                    )
                                    or character == " "
                                )
                            ):
                                window.player_name += character
                            continue
                    if current_screen == "game_over" and event.key in (
                        pygame.K_RETURN, pygame.K_KP_ENTER
                    ):
                        if not save_highscore(
                            config.highscore_filename,
                            scores,
                            window.player_name,
                            game_state.score,
                        ):
                            window.score_error = "Save failed. ENTER: retry"
                            continue
                        window.score_error = ""
                        maze, player, ghosts, game_state = create_game(config)
                        window.last_player_position = None
                        window.show_cheats = False
                        window.noclip_enabled = False
                        window.invincible_enabled = False
                        window.next_level_requested = False
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
                if window.return_to_menu:
                    window.return_to_menu = False
                    maze, player, ghosts, game_state = create_game(config)
                    window.last_player_position = None
                    window.show_cheats = False
                    window.noclip_enabled = False
                    window.invincible_enabled = False
                    window.next_level_requested = False
                    window.animation_frame = 0
                    window.pending_key = -1
                    current_screen = "menu"
                elif not game_state.game_over and not game_state.victory:
                    maze, player, ghosts, game_state = create_game(
                        config,
                        level_number=game_state.level,
                        score=game_state.score,
                        lives=player.lives,
                    )
                    window.last_player_position = None
                    window.animation_frame = 0
                    window.pending_key = -1
                else:
                    window.player_name = ""
                    window.score_error = ""
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
                scores,
            )
            if current_screen == "game_over":
                name_image = render_text(
                    window.fonts["text"], f"Name: {window.player_name}"
                )
                width, _ = name_image.get_size()
                window.screen.blit(
                    name_image,
                    ((resources.WINDOW_WIDTH - width) // 2, scaled(390)),
                )
                if window.score_error:
                    error_image = render_text(
                        window.fonts["text"], window.score_error
                    )
                    error_width, _ = error_image.get_size()
                    window.screen.blit(
                        error_image,
                        (
                            (resources.WINDOW_WIDTH - error_width) // 2,
                            scaled(440),
                        ),
                    )
            window.refresh()
            frame_elapsed = time.perf_counter() - frame_start
            time.sleep(max(0, 1 / 60 - frame_elapsed))

    finally:
        pygame.quit()
