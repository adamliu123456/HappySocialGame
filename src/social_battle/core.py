from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import exp


class Terrain(str, Enum):
    PLAIN = "plain"
    FOREST = "forest"
    FORT = "fort"


@dataclass
class GameConfig:
    width: int = 5
    height: int = 5
    max_hp: int = 10
    max_turn_time_sec: int = 20


@dataclass
class Player:
    player_id: str
    name: str
    hp: int = 10
    rating: float = 1200
    rd: float = 300
    position: tuple[int, int] = (0, 0)


@dataclass
class Board:
    width: int
    height: int
    terrain: list[list[Terrain]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.terrain:
            self.terrain = [[Terrain.PLAIN for _ in range(self.width)] for _ in range(self.height)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def defense_bonus(self, x: int, y: int) -> int:
        tile = self.terrain[y][x]
        if tile == Terrain.FOREST:
            return 1
        if tile == Terrain.FORT:
            return 2
        return 0


@dataclass
class TurnAction:
    move: tuple[int, int] | None = None
    attack: bool = False
    skill: str | None = None


@dataclass
class MatchResult:
    winner_id: str | None
    turns: int
    reason: str


def _is_adjacent(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


def resolve_turn(board: Board, acting: Player, target: Player, action: TurnAction) -> None:
    if action.move:
        nx, ny = acting.position[0] + action.move[0], acting.position[1] + action.move[1]
        if board.in_bounds(nx, ny) and abs(action.move[0]) + abs(action.move[1]) <= 1:
            acting.position = (nx, ny)

    if action.attack and _is_adjacent(acting.position, target.position):
        damage = 2 - board.defense_bonus(*target.position)
        target.hp -= max(1, damage)

    if action.skill == "dash":
        nx = min(board.width - 1, acting.position[0] + 1)
        acting.position = (nx, acting.position[1])
    elif action.skill == "shield":
        acting.hp = min(10, acting.hp + 1)


def update_elo(a: Player, b: Player, a_win: float, k: int = 32) -> None:
    expected_a = 1 / (1 + 10 ** ((b.rating - a.rating) / 400))
    expected_b = 1 - expected_a
    a.rating += k * (a_win - expected_a)
    b.rating += k * ((1 - a_win) - expected_b)


def update_glicko_rd(player: Player, inactive_days: int = 0) -> None:
    # 简化版：长期未活跃会增加不确定度 RD
    player.rd = min(350, player.rd + inactive_days * 2)


def trueskill_like_quality(mus: list[float], sigmas: list[float]) -> float:
    # 用于多人房匹配质量估计（简化版）
    avg_mu = sum(mus) / len(mus)
    uncertainty = sum(sigmas) / len(sigmas)
    spread = sum(abs(mu - avg_mu) for mu in mus) / len(mus)
    return 1 / (1 + exp((spread + uncertainty / 100 - 4)))


@dataclass
class MonetizationPlan:
    pure_cosmetic: bool = True
    has_battle_pass: bool = True
    has_lootbox: bool = False
    probability_disclosure_required: bool = True

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.has_lootbox and not self.probability_disclosure_required:
            issues.append("启用随机抽取时必须披露概率。")
        if not self.pure_cosmetic:
            issues.append("MVP阶段建议避免付费影响公平。")
        return issues
