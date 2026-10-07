from src.utils import possible_neighbor, mirror_path
from collections import deque
import random


def bfs(start: tuple[int, int], target: tuple[int, int],
        maze: list[list[int]]) -> list[tuple[int, int]]:
    y: int = start[0]
    x: int = start[1]

    line: deque[tuple[int, int]] = deque()
    visited: list[tuple[int, int]] = []
    routing_table: dict[tuple[int, int], tuple[int, int]] = {}

    while True:

        if (y, x) == target:
            return road_construction(routing_table, start, target)

        if (y, x) not in visited:

            cell: int = maze[y][x]
            neighbor: list[
                tuple[int, int]] | None = possible_neighbor(cell, y, x)
            if neighbor:
                for tp in neighbor:
                    if tp not in visited and tp not in line:
                        line.append(tp)
                        routing_table[tp] = (y, x)

            visited.append((y, x))

        if bool(line) is not True:
            return []
        position: tuple[int, int] = line.popleft()
        y = position[0]
        x = position[1]


def road_construction(routing_table: dict[tuple[int, int], tuple[int, int]],
                      start: tuple[int, int],
                      target: tuple[int, int]) -> list[tuple[int, int]]:
    final_path: list[tuple[int, int]] = []
    final_path.append(target)
    point: tuple[int, int] = target

    while True:

        if point == start:
            return final_path[::-1]
        point = routing_table[point]
        final_path.append(point)


def preshoot(pos_player: tuple[int, int],
             maze: list[list[int]]) -> tuple[int, int]:
    y: int = pos_player[0]
    x: int = pos_player[1]
    cell_player: int = maze[y][x]
    neighbor_player: list[tuple[int, int]] | None = []
    target: tuple[int, int] = pos_player
    multi: int = random.randint(1, 4)

    for i in range(multi):
        neighbor_player = possible_neighbor(cell_player, y, x)
        if neighbor_player:
            target = random.choice(neighbor_player)
            y = target[0]
            x = target[1]
            cell_player = maze[y][x]
    return target


def move_randomly(path: dict[str, int],
                  last_path: str | None) -> str | None:
    direction: list[str] = []

    for key, value in path.items():
        if value == 1:
            direction.append(key)

    if not direction:
        return None

    if mirror_path(last_path) in direction and len(direction) > 1:
        direction.remove(mirror_path(last_path))

    return random.choice(direction)


def unpredictable(start: tuple[int, int], pos_player: tuple[int, int],
                  maze: list[list[int]]) -> tuple[int, int]:
    nb: int = random.randint(1, 100)
    if nb <= 70:
        target: list[tuple[int, int]] = bfs(start, pos_player, maze)

        return target[1]
    wall: int = maze[start[0]][start[1]]
    possible_choice: list[tuple[int, int]] | None = possible_neighbor(
        wall, start[0], start[1])

    if possible_choice:
        return random.choice(possible_choice)

    return pos_player


def to_flee(pos_ghost: tuple[int, int], pos_player: tuple[int, int],
            last_pos_ghost: tuple[int, int] | None,
            maze: list[list[int]]) -> tuple[int, int]:

    route: list[tuple[int, int]] = bfs(pos_ghost, pos_player, maze)

    if pos_ghost == pos_player:
        return pos_ghost

    if route:
        cell_ghost: tuple[int, int] = route[0]
        cell: int = maze[cell_ghost[0]][cell_ghost[1]]

        neighbor_ghost: list[tuple[int, int]] | None = possible_neighbor(
            cell, pos_ghost[0], pos_ghost[1])

        if neighbor_ghost:

            if len(neighbor_ghost) > 1 and last_pos_ghost in neighbor_ghost:
                neighbor_ghost.remove(last_pos_ghost)

            if len(neighbor_ghost) > 1 and route[1] in neighbor_ghost:
                neighbor_ghost.remove(route[1])
            return random.choice(neighbor_ghost)

        return cell_ghost
    return pos_ghost
