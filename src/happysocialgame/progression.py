from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SeasonTask:
    task_id: str
    description: str
    target: int
    progress: int = 0
    reward_xp: int = 100

    @property
    def completed(self) -> bool:
        return self.progress >= self.target

    def apply(self, delta: int) -> int:
        before = self.completed
        self.progress = min(self.target, self.progress + max(delta, 0))
        if (not before) and self.completed:
            return self.reward_xp
        return 0


@dataclass
class BattlePass:
    season_id: str
    level: int = 1
    xp: int = 0
    premium_unlocked: bool = False
    xp_per_level: int = 500
    tasks: Dict[str, SeasonTask] = field(default_factory=dict)
    claimed_levels: List[int] = field(default_factory=list)

    def add_task(self, task: SeasonTask) -> None:
        self.tasks[task.task_id] = task

    def report_task_progress(self, task_id: str, delta: int) -> int:
        task = self.tasks[task_id]
        gained = task.apply(delta)
        if gained:
            self.add_xp(gained)
        return gained

    def add_xp(self, amount: int) -> None:
        self.xp += max(amount, 0)
        while self.xp >= self.xp_per_level:
            self.xp -= self.xp_per_level
            self.level += 1

    def claim_level_reward(self, level: int) -> bool:
        if level > self.level or level in self.claimed_levels:
            return False
        self.claimed_levels.append(level)
        return True
