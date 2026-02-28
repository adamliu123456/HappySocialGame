from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MatchTicket:
    player_id: str
    rating: float
    mode: str
    party_size: int = 1
    created_at: float = field(default_factory=time.time)


@dataclass
class MatchmakerConfig:
    initial_rating_window: int = 80
    window_growth_per_20s: int = 40


class Matchmaker:
    def __init__(self, config: Optional[MatchmakerConfig] = None) -> None:
        self.config = config or MatchmakerConfig()
        self._queues: Dict[str, List[MatchTicket]] = {}

    def enqueue(self, ticket: MatchTicket) -> None:
        self._queues.setdefault(ticket.mode, []).append(ticket)

    def pop_match(self, mode: str, required_players: int) -> Optional[List[MatchTicket]]:
        queue = self._queues.get(mode, [])
        if len(queue) < required_players:
            return None

        queue.sort(key=lambda t: t.created_at)

        for i, anchor in enumerate(queue):
            elapsed = max(0.0, time.time() - anchor.created_at)
            expansion_steps = int(elapsed // 20)
            rating_window = self.config.initial_rating_window + (
                expansion_steps * self.config.window_growth_per_20s
            )

            candidates = [anchor]
            for j, other in enumerate(queue):
                if i == j:
                    continue
                if abs(other.rating - anchor.rating) <= rating_window:
                    candidates.append(other)
                if len(candidates) == required_players:
                    break

            if len(candidates) == required_players:
                used_ids = {t.player_id for t in candidates}
                self._queues[mode] = [t for t in queue if t.player_id not in used_ids]
                return candidates

        return None

    def queue_size(self, mode: str) -> int:
        return len(self._queues.get(mode, []))
