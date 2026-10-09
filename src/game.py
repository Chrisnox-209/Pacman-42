"""Game objects, initialization"""


class GameState:
    def __init__(self, score: int,
                 level: int,
                 remaining_time: int,
                 frightened: bool,
                 game_over: bool,
                 cheat: bool) -> None:
        self.score: int = score
        self.level: int = level
        self.remaining_time: int = remaining_time
        self.cheat: bool = cheat
        self.game_over: bool = game_over
        self.frightened: bool = frightened


class Player:
    def __init__(self, x: int, y: int,
                 spawn_position: tuple[int, int],
                 direction: tuple[int, int],
                 lives: int,) -> None:
        self.x: int = x
        self.y: int = y
        self.spawn_position: tuple[int, int] = spawn_position
        self.direction: tuple[int, int] = direction
        self.lives: int = lives
