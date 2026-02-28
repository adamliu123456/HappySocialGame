from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


Position = Tuple[int, int]


class ActionType(str, Enum):
    MOVE = "move"
    ATTACK = "attack"
    SKILL = "skill"


@dataclass
class Unit:
    unit_id: str
    player_id: str
    hp: int
    attack: int
    move_range: int
    skill_damage: int
    cooldown: int = 0
    position: Position = (0, 0)

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass
class Action:
    unit_id: str
    action_type: ActionType
    target: Position


@dataclass
class GameState:
    width: int = 5
    height: int = 5
    turn: int = 1
    current_player: str = "p1"
    winner: Optional[str] = None
    units: Dict[str, Unit] = field(default_factory=dict)
    turn_log: List[str] = field(default_factory=list)

    def unit_at(self, pos: Position) -> Optional[Unit]:
        for unit in self.units.values():
            if unit.alive and unit.position == pos:
                return unit
        return None

    def enemy_units(self, player_id: str) -> List[Unit]:
        return [u for u in self.units.values() if u.player_id != player_id and u.alive]

    def friend_units(self, player_id: str) -> List[Unit]:
        return [u for u in self.units.values() if u.player_id == player_id and u.alive]


class RuleError(ValueError):
    pass


class BoardGameEngine:
    def __init__(self, state: GameState):
        self.state = state

    def _in_bounds(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self.state.width and 0 <= y < self.state.height

    def _distance(self, a: Position, b: Position) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def submit_action(self, player_id: str, action: Action) -> None:
        if self.state.winner:
            raise RuleError("game is over")
        if player_id != self.state.current_player:
            raise RuleError("not your turn")
        if action.unit_id not in self.state.units:
            raise RuleError("unknown unit")

        unit = self.state.units[action.unit_id]
        if unit.player_id != player_id:
            raise RuleError("cannot control enemy unit")
        if not unit.alive:
            raise RuleError("unit is dead")
        if not self._in_bounds(action.target):
            raise RuleError("target out of bounds")

        if action.action_type == ActionType.MOVE:
            self._apply_move(unit, action.target)
        elif action.action_type == ActionType.ATTACK:
            self._apply_attack(unit, action.target)
        elif action.action_type == ActionType.SKILL:
            self._apply_skill(unit, action.target)
        else:
            raise RuleError("unsupported action")

        self._tick_cooldown(player_id)
        self._next_turn()
        self._check_winner()

    def _apply_move(self, unit: Unit, target: Position) -> None:
        if self.state.unit_at(target):
            raise RuleError("target tile occupied")
        if self._distance(unit.position, target) > unit.move_range:
            raise RuleError("move too far")
        old = unit.position
        unit.position = target
        self.state.turn_log.append(f"{unit.unit_id} move {old}->{target}")

    def _apply_attack(self, unit: Unit, target: Position) -> None:
        enemy = self.state.unit_at(target)
        if not enemy or enemy.player_id == unit.player_id:
            raise RuleError("no enemy at target")
        if self._distance(unit.position, target) > 1:
            raise RuleError("attack out of range")
        enemy.hp -= unit.attack
        self.state.turn_log.append(f"{unit.unit_id} attack {enemy.unit_id} dmg={unit.attack}")

    def _apply_skill(self, unit: Unit, target: Position) -> None:
        if unit.cooldown > 0:
            raise RuleError("skill on cooldown")
        enemy = self.state.unit_at(target)
        if not enemy or enemy.player_id == unit.player_id:
            raise RuleError("no enemy at target")
        if self._distance(unit.position, target) > 2:
            raise RuleError("skill out of range")
        enemy.hp -= unit.skill_damage
        unit.cooldown = 2
        self.state.turn_log.append(f"{unit.unit_id} skill {enemy.unit_id} dmg={unit.skill_damage}")

    def _tick_cooldown(self, player_id: str) -> None:
        for u in self.state.friend_units(player_id):
            if u.cooldown > 0:
                u.cooldown -= 1

    def _next_turn(self) -> None:
        players = sorted({u.player_id for u in self.state.units.values()})
        idx = players.index(self.state.current_player)
        self.state.current_player = players[(idx + 1) % len(players)]
        self.state.turn += 1

    def _check_winner(self) -> None:
        alive_players = sorted({u.player_id for u in self.state.units.values() if u.alive})
        if len(alive_players) == 1:
            self.state.winner = alive_players[0]


def create_mirror_opening() -> GameState:
    """第一局镜像阵容示例。"""
    state = GameState()
    state.units = {
        "p1_u1": Unit("p1_u1", "p1", hp=10, attack=3, move_range=1, skill_damage=4, position=(0, 0)),
        "p1_u2": Unit("p1_u2", "p1", hp=8, attack=2, move_range=2, skill_damage=3, position=(0, 1)),
        "p2_u1": Unit("p2_u1", "p2", hp=10, attack=3, move_range=1, skill_damage=4, position=(4, 4)),
        "p2_u2": Unit("p2_u2", "p2", hp=8, attack=2, move_range=2, skill_damage=3, position=(4, 3)),
    }
    return state
