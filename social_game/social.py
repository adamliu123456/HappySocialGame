from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Guild:
    guild_id: str
    name: str
    members: List[str] = field(default_factory=list)
    announcements: List[str] = field(default_factory=list)


class SocialHub:
    def __init__(self) -> None:
        self.friends: Dict[str, set[str]] = {}
        self.guilds: Dict[str, Guild] = {}
        self.replays: Dict[str, List[str]] = {}

    def add_friend(self, user_id: str, other_id: str) -> None:
        self.friends.setdefault(user_id, set()).add(other_id)
        self.friends.setdefault(other_id, set()).add(user_id)

    def create_guild(self, guild_id: str, name: str, owner_id: str) -> Guild:
        guild = Guild(guild_id=guild_id, name=name, members=[owner_id])
        self.guilds[guild_id] = guild
        return guild

    def add_member(self, guild_id: str, user_id: str) -> None:
        guild = self.guilds[guild_id]
        if user_id not in guild.members:
            guild.members.append(user_id)

    def save_replay_event(self, room_id: str, event: str) -> None:
        self.replays.setdefault(room_id, []).append(event)
