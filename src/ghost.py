from src.utils import convert_wall, mirror_path
import random


class Ghost:
    def __init__(self, x: int, y: int,
                 spawn_position: tuple[int, int],
                 name: str) -> None:

        self.x: int = x
        self.y: int = y
        self.spawn_position: tuple[int, int] = spawn_position
        self.name: str = name

    def move_to_direction(self, direction: str) -> None:
        if direction == "N":
            self.y = self.y - 1
        elif direction == "S":
            self.y = self.y + 1
        elif direction == "E":
            self.x = self.x + 1
        elif direction == "W":
            self.x = self.x - 1

    def move_to_position(self, position: tuple[int, int]) -> None:
        self.y = position[0]
        self.x = position[1]

    def check_path(self, maze: list[list[int]]) -> dict[str, int] | None:
        wall: int = maze[self.y][self.x]
        return convert_wall(wall)

    def move(self, path: dict[str, int], last_path: str) -> str | None:
        direction: list[str] = []

        for key, value in path.items():
            if value == 1:
                direction.append(key)

        if not direction:
            return None

        if mirror_path(last_path) in direction and len(direction) > 1:
            direction.remove(mirror_path(last_path))

        return random.choice(direction)
