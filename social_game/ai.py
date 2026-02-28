from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .engine import GameRoom, PlayerAction


@dataclass
class BotPolicy:
    player_id: str

    def choose_action(self, room: GameRoom) -> PlayerAction:
        enemy_id = next(pid for pid in room.players if pid != self.player_id)
        best = None

        for i, unit in enumerate(room.players[self.player_id].units):
            for tx, ty in room.legal_moves(self.player_id, i):
                score = self._score_move(room, enemy_id, tx, ty)
                if best is None or score > best[0]:
                    use_skill = score >= 8 and not unit.skill_used
                    best = (score, PlayerAction(self.player_id, i, tx, ty, use_skill=use_skill))

        if best is None:
            return PlayerAction(self.player_id, 0, 0, 0)
        return best[1]

    def _score_move(self, room: GameRoom, enemy_id: str, tx: int, ty: int) -> int:
        score = 0
        if (tx, ty) in room.control_points:
            score += 6
        for enemy in room.players[enemy_id].units:
            if (enemy.x, enemy.y) == (tx, ty):
                score += 7
            dist = abs(enemy.x - tx) + abs(enemy.y - ty)
            score += max(0, 3 - dist)
        return score
