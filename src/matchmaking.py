from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PlayerTicket:
    player_id: str
    rating: int
    newbie_games: int
    wait_seconds: int = 0


@dataclass
class MatchmakingQueue:
    base_window: int = 80
    newbie_limit: int = 10
    queue: List[PlayerTicket] = field(default_factory=list)

    def enqueue(self, ticket: PlayerTicket) -> None:
        self.queue.append(ticket)

    def tick(self, seconds: int = 1) -> None:
        for t in self.queue:
            t.wait_seconds += seconds

    def pop_match(self) -> Optional[Tuple[PlayerTicket, PlayerTicket]]:
        if len(self.queue) < 2:
            return None

        best_pair: Optional[Tuple[int, int, int]] = None  # i, j, diff
        for i in range(len(self.queue)):
            for j in range(i + 1, len(self.queue)):
                a, b = self.queue[i], self.queue[j]
                if not self._same_pool(a, b):
                    continue
                diff = abs(a.rating - b.rating)
                win = self._window_for(a, b)
                if diff <= win:
                    if not best_pair or diff < best_pair[2]:
                        best_pair = (i, j, diff)

        if not best_pair:
            return None

        i, j, _ = best_pair
        b = self.queue.pop(j)
        a = self.queue.pop(i)
        return a, b

    def _same_pool(self, a: PlayerTicket, b: PlayerTicket) -> bool:
        a_newbie = a.newbie_games < self.newbie_limit
        b_newbie = b.newbie_games < self.newbie_limit
        return a_newbie == b_newbie

    def _window_for(self, a: PlayerTicket, b: PlayerTicket) -> int:
        extra = min(a.wait_seconds, b.wait_seconds) // 5 * 20
        return self.base_window + extra


@dataclass
class TeamSynergyRecord:
    """2v2 组队协同因子，越高代表固定队默契越高。"""

    pair_synergy: Dict[Tuple[str, str], float] = field(default_factory=dict)

    def get(self, p1: str, p2: str) -> float:
        key = tuple(sorted((p1, p2)))
        return self.pair_synergy.get(key, 0.0)

    def record_win(self, p1: str, p2: str) -> None:
        key = tuple(sorted((p1, p2)))
        self.pair_synergy[key] = self.pair_synergy.get(key, 0.0) + 0.1
