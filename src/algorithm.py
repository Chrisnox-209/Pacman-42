from src.utils import possible_neighbor
from collections import deque


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

        print(f"line: {line}")
        print("visited: ", visited)
        print(f"new pos --> : {position}")


def road_construction(routing_table: dict[tuple[int, int], tuple[int, int]],
                      start: tuple[int, int],
                      target: tuple[int, int]) -> list[tuple[int, int]]:
    final_path: list[tuple[int, int]] = []
    final_path.append(target)
    point: tuple[int, int] = target

    while True:

        if point == start:
            print(final_path[::-1])
            return final_path[::-1]
        point = routing_table[point]
        final_path.append(point)
