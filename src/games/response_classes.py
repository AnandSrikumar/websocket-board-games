from dataclasses import dataclass
from enum import Enum


@dataclass
class MakeMoveResponse:
    match_id: int
    move: dict
    move_maker: int
    message: str
    is_success: bool


@dataclass
class GameResult:
    match_id: int
    win_state: dict
    winner: int | None = None
    is_finished: bool = False
