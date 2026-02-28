from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Tuple


class RatingSystem(Protocol):
    def update_1v1(self, a: float, b: float, result_for_a: float) -> Tuple[float, float]:
        ...


@dataclass
class EloRating:
    k: int = 32

    def expected(self, a: float, b: float) -> float:
        return 1.0 / (1.0 + 10 ** ((b - a) / 400.0))

    def update_1v1(self, a: float, b: float, result_for_a: float) -> Tuple[float, float]:
        ea = self.expected(a, b)
        eb = 1.0 - ea
        na = a + self.k * (result_for_a - ea)
        nb = b + self.k * ((1.0 - result_for_a) - eb)
        return na, nb


@dataclass
class LadderProfile:
    player_id: str
    rating: float = 1000.0
    rd: float = 350.0  # 预留给 Glicko 的评分偏差
    games: int = 0


def settle_match_1v1(winner: LadderProfile, loser: LadderProfile, system: RatingSystem) -> None:
    new_winner, new_loser = system.update_1v1(winner.rating, loser.rating, 1.0)
    winner.rating = round(new_winner, 2)
    loser.rating = round(new_loser, 2)
    winner.games += 1
    loser.games += 1
