from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class PlayerRating:
    mu: float = 25.0
    sigma: float = 8.333


class EloRating:
    def __init__(self, k: float = 32.0):
        self.k = k

    def update(self, ra: float, rb: float, score_a: float) -> tuple[float, float]:
        expected_a = 1.0 / (1 + 10 ** ((rb - ra) / 400))
        new_ra = ra + self.k * (score_a - expected_a)
        new_rb = rb + self.k * ((1 - score_a) - (1 - expected_a))
        return new_ra, new_rb


class TrueSkillLite:
    """Lightweight approximation suitable for MVP leaderboard without third-party deps."""

    def __init__(self, beta: float = 4.166, tau: float = 0.083):
        self.beta = beta
        self.tau = tau

    def update_1v1(self, a: PlayerRating, b: PlayerRating, a_wins: bool) -> tuple[PlayerRating, PlayerRating]:
        c = math.sqrt(2 * self.beta**2 + a.sigma**2 + b.sigma**2)
        delta_mu = a.mu - b.mu
        expected = 1 / (1 + math.exp(-delta_mu / c))
        outcome = 1.0 if a_wins else 0.0
        k_a = (a.sigma**2 + self.tau**2) / c
        k_b = (b.sigma**2 + self.tau**2) / c

        new_a = PlayerRating(
            mu=a.mu + k_a * (outcome - expected),
            sigma=max(1.0, a.sigma * 0.97),
        )
        new_b = PlayerRating(
            mu=b.mu + k_b * ((1 - outcome) - (1 - expected)),
            sigma=max(1.0, b.sigma * 0.97),
        )
        return new_a, new_b
