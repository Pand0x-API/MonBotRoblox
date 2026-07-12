from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    discord_id: str
    roblox_id: int | None = None
    roblox_username: str | None = None
    verified: bool = False
    created_at: datetime = datetime.now()


@dataclass
class GamePlayer:
    roblox_id: int
    coins: int = 0
    level: int = 1
