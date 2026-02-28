from __future__ import annotations

from typing import List

from .engine import GameRoom


def render_board(room: GameRoom, player_a: str, player_b: str) -> str:
    grid: List[List[str]] = [["." for _ in range(room.width)] for _ in range(room.height)]

    for cx, cy in room.control_points:
        grid[cy][cx] = "*"

    for unit in room.players[player_a].units:
        grid[unit.y][unit.x] = unit.symbol
    for unit in room.players[player_b].units:
        current = grid[unit.y][unit.x]
        grid[unit.y][unit.x] = current.lower() if current != "." else unit.symbol.lower()

    lines = ["   " + " ".join(str(x) for x in range(room.width))]
    for y in range(room.height):
        lines.append(f"{y}: " + " ".join(grid[y]))
    return "\n".join(lines)
