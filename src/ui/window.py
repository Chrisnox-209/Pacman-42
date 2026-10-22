"""Manage the Pygame window, gameplay input, and pause screen."""

import curses
import time

import pygame

from . import resources
from .resources import create_display
from .screens import draw_message


class GameWindow:
    """Provide the input method expected by the original game loop."""

    def __init__(self) -> None:
        """Create the display and initialize input and interface state."""
        self.screen, self.fonts, self.images = create_display()
        self.closed: bool = False
        self.animation_frame = 0
        self.pending_key = -1
        self.last_player_position: tuple[int, int] | None = None
        self.last_move_time: float = 0.0
        self.return_to_menu: bool = False
        self.show_cheats: bool = False
        self.noclip_enabled: bool = False
        self.invincible_enabled: bool = False
        self.next_level_requested: bool = False
        self.player_name: str = ""
        self.score_error: str = ""
        self.pause_duration: float = 0.0

    def refresh(self) -> None:
        """Display the frame directly, without resizing it."""
        pygame.display.flip()

    def getch(self) -> int:
        """Translate Pygame input into the original terminal key codes."""
        if self.return_to_menu:
            return ord("q")

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
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_c:
                    self.show_cheats = not self.show_cheats
                elif event.key == pygame.K_n:
                    self.noclip_enabled = not self.noclip_enabled
                elif event.key == pygame.K_i:
                    self.invincible_enabled = not self.invincible_enabled
                    print("INVINCIBLE:", self.invincible_enabled)
                elif event.key == pygame.K_l:
                    self.next_level_requested = not self.next_level_requested
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.closed = True
                elif event.key == pygame.K_ESCAPE:
                    pause_start = time.monotonic()
                    self.pause()
                    self.pause_duration += time.monotonic() - pause_start
                elif event.key in arrow_keys:
                    key = arrow_keys[event.key]
                elif event.unicode:
                    key = ord(event.unicode[0])

        if self.closed or self.return_to_menu:
            return ord("q")

        return key

    def pause(self) -> None:
        """Wait for the user to resume without updating game objects."""
        while not self.closed:
            frame_start = time.perf_counter()
            self.screen.blit(resources.BACKGROUND_IMAGE, (0, 0))
            draw_message(
                self.screen,
                self.fonts,
                "PAUSED",
                ("ENTER: resume", "ESC: return to menu", "Q: quit"),
            )
            self.refresh()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.closed = True
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return

                    if event.key == pygame.K_ESCAPE:
                        self.return_to_menu = True
                        return

                    if event.key == pygame.K_q:
                        self.closed = True

            frame_elapsed = time.perf_counter() - frame_start
            time.sleep(max(0, 1 / 60 - frame_elapsed))
