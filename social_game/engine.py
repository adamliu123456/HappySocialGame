from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class UnitType(str, Enum):
    SCOUT = "scout"
    BRUISER = "bruiser"


@dataclass
class Unit:
    owner_id: str
    unit_type: UnitType
    hp: int
    attack: int
    move_range: int
    x: int
    y: int

    @classmethod
    def spawn(cls, owner_id: str, unit_type: UnitType, x: int, y: int) -> "Unit":
        if unit_type == UnitType.SCOUT:
            return cls(owner_id=owner_id, unit_type=unit_type, hp=6, attack=2, move_range=2, x=x, y=y)
        return cls(owner_id=owner_id, unit_type=unit_type, hp=10, attack=3, move_range=1, x=x, y=y)


@dataclass
class PlayerAction:
    player_id: str
    unit_index: int
    target_x: int
    target_y: int
    use_skill: bool = False


@dataclass
class PlayerState:
    player_id: str
    units: List[Unit] = field(default_factory=list)


@dataclass
class TurnResult:
    events: List[str]
    winner: Optional[str]


class GameRoom:
    """Prototype B: asynchronous board raid room (2 players)."""

    width: int = 5
    height: int = 5
    max_turns: int = 20

    def __init__(self, room_id: str, player_a: str, player_b: str):
        self.room_id = room_id
        self.turn = 1
        self.players: Dict[str, PlayerState] = {
            player_a: PlayerState(player_id=player_a),
            player_b: PlayerState(player_id=player_b),
        }
        self.pending_actions: Dict[str, PlayerAction] = {}
        self.control_points: List[Tuple[int, int]] = [(2, 2)]
        self.score: Dict[str, int] = {player_a: 0, player_b: 0}

        self.players[player_a].units = [
            Unit.spawn(player_a, UnitType.SCOUT, 0, 0),
            Unit.spawn(player_a, UnitType.BRUISER, 0, 1),
        ]
        self.players[player_b].units = [
            Unit.spawn(player_b, UnitType.SCOUT, 4, 4),
            Unit.spawn(player_b, UnitType.BRUISER, 4, 3),
        ]

    def submit_action(self, action: PlayerAction) -> None:
        if action.player_id not in self.players:
            raise ValueError("unknown player")
        self.pending_actions[action.player_id] = action

    def ready_to_resolve(self) -> bool:
        return len(self.pending_actions) == 2

    def resolve_turn(self) -> TurnResult:
        if not self.ready_to_resolve():
            raise RuntimeError("both players must submit action")

        events: List[str] = []
        for player_id, action in self.pending_actions.items():
            actor = self.players[player_id]
            if action.unit_index >= len(actor.units):
                events.append(f"{player_id} invalid unit index, skipped")
                continue
            unit = actor.units[action.unit_index]
            dist = abs(unit.x - action.target_x) + abs(unit.y - action.target_y)
            if dist <= unit.move_range and self._inside(action.target_x, action.target_y):
                unit.x, unit.y = action.target_x, action.target_y
                events.append(f"{player_id} moved {unit.unit_type} to {(unit.x, unit.y)}")

            enemy = self._enemy_player(player_id)
            target = self._unit_at(enemy, unit.x, unit.y)
            if target is not None:
                damage = unit.attack + (1 if action.use_skill else 0)
                target.hp -= damage
                events.append(f"{player_id} hit enemy for {damage} damage")

        self._cleanup_dead_units(events)
        self._score_control_points(events)
        winner = self._winner()
        self.turn += 1
        self.pending_actions.clear()

        return TurnResult(events=events, winner=winner)

    def _inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _enemy_player(self, player_id: str) -> str:
        return next(pid for pid in self.players if pid != player_id)

    def _unit_at(self, player_id: str, x: int, y: int) -> Optional[Unit]:
        for unit in self.players[player_id].units:
            if unit.x == x and unit.y == y:
                return unit
        return None

    def _cleanup_dead_units(self, events: List[str]) -> None:
        for player_id, state in self.players.items():
            before = len(state.units)
            state.units = [u for u in state.units if u.hp > 0]
            if len(state.units) < before:
                events.append(f"{player_id} lost {before - len(state.units)} unit(s)")

    def _score_control_points(self, events: List[str]) -> None:
        for point in self.control_points:
            owners = []
            for player_id, state in self.players.items():
                if any((u.x, u.y) == point for u in state.units):
                    owners.append(player_id)
            if len(owners) == 1:
                self.score[owners[0]] += 1
                events.append(f"{owners[0]} captured control point {point}")

    def _winner(self) -> Optional[str]:
        living = [pid for pid, s in self.players.items() if s.units]
        if len(living) == 1:
            return living[0]
        if self.turn >= self.max_turns:
            return max(self.score, key=self.score.get)
        return None

    def snapshot(self) -> dict:
        return {
            "room_id": self.room_id,
            "turn": self.turn,
            "score": self.score,
            "players": {
                pid: [
                    {
                        "type": u.unit_type.value,
                        "hp": u.hp,
                        "atk": u.attack,
                        "pos": [u.x, u.y],
                    }
                    for u in state.units
                ]
                for pid, state in self.players.items()
            },
        }
