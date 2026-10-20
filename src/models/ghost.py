"""Store ghost attributes and update their positions."""

from src.common.utils import convert_wall


class Ghost:
    """Store ghost coordinates, spawn, identity, and behavior state."""

    def __init__(self, x: int, y: int,
                 spawn_position: tuple[int, int],
                 name: str,
                 state: str) -> None:
        """Initialize position, spawn, name, and behavior state."""
        self.x: int = x
        self.y: int = y
        self.spawn_position: tuple[int, int] = spawn_position
        self.name: str = name
        self.state: str = state

    def move_to_direction(self, direction: str) -> None:
        """Move one cell in the given cardinal direction."""
        if direction == "N":
            self.y = self.y - 1
        elif direction == "S":
            self.y = self.y + 1
        elif direction == "E":
            self.x = self.x + 1
        elif direction == "W":
            self.x = self.x - 1

    def move_to_position(self, position: tuple[int, int]) -> None:
        """Set the ghost position from a (row, column) pair."""
        self.y = position[0]
        self.x = position[1]

    def check_path(self, maze: list[list[int]]) -> dict[str, int] | None:
        """Return open directions at the ghost position from the wall mask."""
        wall: int = maze[self.y][self.x]
        return convert_wall(wall)
