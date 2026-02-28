from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


@dataclass
class EloRating:
    value: float = 1500.0

    def expected_score(self, opponent: "EloRating") -> float:
        return 1.0 / (1.0 + 10 ** ((opponent.value - self.value) / 400.0))

    def update(self, opponent: "EloRating", actual_score: float, k: float = 32.0) -> "EloRating":
        expected = self.expected_score(opponent)
        return EloRating(value=self.value + k * (actual_score - expected))


@dataclass
class Glicko2Player:
    rating: float = 1500.0
    rd: float = 350.0
    volatility: float = 0.06

    _SCALE: float = 173.7178
    _TAU: float = 0.5

    @property
    def mu(self) -> float:
        return (self.rating - 1500.0) / self._SCALE

    @property
    def phi(self) -> float:
        return self.rd / self._SCALE

    @staticmethod
    def _g(phi: float) -> float:
        return 1.0 / math.sqrt(1.0 + 3.0 * phi * phi / (math.pi * math.pi))

    @classmethod
    def _e(cls, mu: float, mu_j: float, phi_j: float) -> float:
        return 1.0 / (1.0 + math.exp(-cls._g(phi_j) * (mu - mu_j)))

    def update(self, results: Iterable[Tuple["Glicko2Player", float]]) -> "Glicko2Player":
        results = list(results)
        if not results:
            inflated_phi = math.sqrt(self.phi * self.phi + self.volatility * self.volatility)
            return Glicko2Player(self.rating, inflated_phi * self._SCALE, self.volatility)

        v_inv = 0.0
        delta_sum = 0.0
        for opponent, score in results:
            e_val = self._e(self.mu, opponent.mu, opponent.phi)
            g_val = self._g(opponent.phi)
            v_inv += (g_val**2) * e_val * (1.0 - e_val)
            delta_sum += g_val * (score - e_val)

        v = 1.0 / v_inv
        delta = v * delta_sum
        a = math.log(self.volatility**2)

        def f(x: float) -> float:
            ex = math.exp(x)
            num = ex * (delta * delta - self.phi * self.phi - v - ex)
            den = 2.0 * (self.phi * self.phi + v + ex) ** 2
            return (num / den) - ((x - a) / (self._TAU * self._TAU))

        A = a
        if delta * delta > self.phi * self.phi + v:
            B = math.log(delta * delta - self.phi * self.phi - v)
        else:
            k = 1
            while f(a - k * self._TAU) < 0:
                k += 1
            B = a - k * self._TAU

        fA = f(A)
        fB = f(B)
        while abs(B - A) > 1e-6:
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)
            if fC * fB < 0:
                A = B
                fA = fB
            else:
                fA /= 2.0
            B = C
            fB = fC

        sigma_prime = math.exp(A / 2.0)
        phi_star = math.sqrt(self.phi * self.phi + sigma_prime * sigma_prime)
        phi_prime = 1.0 / math.sqrt((1.0 / (phi_star * phi_star)) + (1.0 / v))

        mu_prime = self.mu + phi_prime * phi_prime * delta_sum
        return Glicko2Player(
            rating=mu_prime * self._SCALE + 1500.0,
            rd=phi_prime * self._SCALE,
            volatility=sigma_prime,
        )


def update_multiplayer_ratings(
    ratings: Sequence[float],
    ranks: Sequence[int],
    k: float = 24.0,
) -> List[float]:
    """
    Simplified multi-player rating update.

    Lower rank value means better result (rank=1 is winner).
    We transform final ranks into pairwise outcomes and accumulate Elo-style updates.
    """
    if len(ratings) != len(ranks):
        raise ValueError("ratings and ranks must have same length")

    new_ratings = list(ratings)
    n = len(ratings)
    for i in range(n):
        delta = 0.0
        for j in range(n):
            if i == j:
                continue
            expected = 1.0 / (1.0 + 10 ** ((ratings[j] - ratings[i]) / 400.0))
            if ranks[i] < ranks[j]:
                score = 1.0
            elif ranks[i] > ranks[j]:
                score = 0.0
            else:
                score = 0.5
            delta += score - expected
        new_ratings[i] = ratings[i] + (k / max(n - 1, 1)) * delta
    return new_ratings
