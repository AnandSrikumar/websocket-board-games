from abc import ABC, abstractmethod

from src.games.response_classes import GameResult, MakeMoveResponse


class GameBase(ABC):
    def __init__(self, match_id: int):
        self._match_id = match_id

    @abstractmethod
    def make_move(self, player_name: str, payload: dict) -> MakeMoveResponse: ...

    @property
    @abstractmethod
    def board(self): ...

    @property
    @abstractmethod
    def match_id(self): ...

    @property
    @abstractmethod
    def players(self): ...

    @abstractmethod
    def get_result(self) -> GameResult: ...

    @abstractmethod
    def add_player(self, player_name: str): ...

    @abstractmethod
    def get_players_stats(self): ...
