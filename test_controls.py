"""Vérifie les déplacements et l'orientation du sprite Pac-Man."""

import importlib.util
import unittest
from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).parent
MODULE_SPEC = importlib.util.spec_from_file_location(
    "pac_man", PROJECT_ROOT / "pac-man.py"
)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
pac_man = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(pac_man)


class PacmanControlsTests(unittest.TestCase):
    """Tests du déplacement et de l'orientation de Pac-Man."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialise Pygame une seule fois pour les tests graphiques."""
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ferme Pygame après tous les tests."""
        pygame.quit()

    def test_movement_in_each_direction(self) -> None:
        """Vérifie le sens et la distance des quatre déplacements."""
        cases = [
            ((400.0, 300.0), (1, 0), (660.0, 300.0)),
            ((400.0, 300.0), (-1, 0), (140.0, 300.0)),
            ((400.0, 300.0), (0, -1), (400.0, 48.0)),
            ((400.0, 300.0), (0, 1), (400.0, 552.0)),
        ]
        for position, direction, expected in cases:
            with self.subTest(direction=direction):
                self.assertEqual(
                    pac_man.move_pacman(position, direction, 1.0), expected
                )

    def test_pacman_stays_inside_window(self) -> None:
        """Vérifie que Pac-Man ne sort pas des bords de la fenêtre."""
        position = pac_man.move_pacman((751.0, 300.0), (1, 0), 1.0)
        self.assertEqual(position, (752.0, 300.0))

    def test_closed_mouth_uses_an_image_asset(self) -> None:
        """Vérifie que l'image bouche fermée est chargée et non dessinée."""
        image = pygame.image.load(
            pac_man.PACMAN_CLOSED_IMAGE_PATH
        ).convert_alpha()
        image = pygame.transform.smoothscale(image, pac_man.PACMAN_SIZE)
        self.assertEqual(image.get_size(), pac_man.PACMAN_SIZE)

    def test_open_mouth_faces_each_movement_direction(self) -> None:
        """Vérifie visuellement l'orientation du sprite dans quatre sens."""
        image = pygame.image.load(pac_man.PACMAN_IMAGE_PATH).convert_alpha()
        image = pygame.transform.smoothscale(image, pac_man.PACMAN_SIZE)
        probes = {
            "right": ((76, 48), (24, 48)),
            "left": ((24, 48), (72, 48)),
            "up": ((48, 24), (48, 72)),
            "down": ((48, 72), (48, 24)),
        }
        for direction, angle in pac_man.ROTATION_ANGLES.items():
            with self.subTest(direction=direction):
                rotated = pygame.transform.rotate(image, angle)
                mouth_probe, solid_probe = probes[direction]
                self.assertLessEqual(rotated.get_at(mouth_probe).a, 80)
                self.assertGreaterEqual(rotated.get_at(solid_probe).a, 180)


if __name__ == "__main__":
    unittest.main()
