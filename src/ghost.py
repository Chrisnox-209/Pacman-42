from src.utils import convert_wall


class Ghost:
    def __init__(
        self,
        x: int,
        y: int,
        spawn_position: tuple[int, int],
        name: str,
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.spawn_position: tuple[int, int] = spawn_position
        self.name: str = name

    def move_to(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def check_path(self, maze) -> dict[str, int] | None:
        wall: int = maze[self.y][self.x]
        return convert_wall(wall)
