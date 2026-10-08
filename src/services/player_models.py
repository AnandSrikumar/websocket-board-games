from dataclasses import dataclass
from uuid import UUID

from fastapi import WebSocket


@dataclass
class PlayerSession:
    player_id: UUID
    websocket: WebSocket
    game_id: UUID
    game_name: str
    player_name: str
    target_wins: int = 10
    connected: bool = True
