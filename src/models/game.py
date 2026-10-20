"""Store player attributes and shared game state."""


class GameState:
    """Store scores, pellets, timers, and game outcome flags."""

    def __init__(self, score: int,
                 position_pacgum: dict[tuple[int, int], bool],
                 position_super_pacgum: dict[tuple[int, int], bool],
                 level: int,
                 remaining_time: int,
                 frightened: bool,
                 game_over: bool,
                 victory: bool,
                 cheat: bool) -> None:
        """Initialize scores, pellet maps, timers, and outcome flags."""
        self.score: int = score
        self.position_pacgum: dict[tuple[int, int], bool] = position_pacgum
        self.position_super_pacgum: dict[tuple[int, int],
                                         bool] = position_super_pacgum
        self.level: int = level
        self.remaining_time: int = remaining_time
        self.cheat: bool = cheat
        self.game_over: bool = game_over
        self.victory: bool = victory
        self.frightened: bool = frightened


class Player:
    """Store player coordinates, spawn, direction, and remaining lives."""

    def __init__(self, x: int, y: int,
                 spawn_position: tuple[int, int],
                 direction: tuple[int, int],
                 lives: int,) -> None:
        """Initialize position, spawn, direction, and remaining lives."""
        self.x: int = x
        self.y: int = y
        self.spawn_position: tuple[int, int] = spawn_position
        self.direction: tuple[int, int] = direction
        self.lives: int = lives
