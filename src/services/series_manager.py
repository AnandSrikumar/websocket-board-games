from dataclasses import asdict
from uuid import UUID

from src.games.game_factory import get_game
from src.games.game import GameBase
from src.log import get_logger
log = get_logger(__name__)

class SeriesManager:
    def __init__(self, series_id, player1, player2, target_wins, game):
        self._player1 = player1
        self._player2 = player2
        self._series_id = series_id
        self._target_wins = target_wins
        self._game = game
        self._game_object: GameBase = get_game(game, series_id)

    async def make_move(self, player_id: UUID, message:dict):
        movement = self._game_object.make_move(player_id, message)
        log.info(f"Movement info: {asdict(movement)}")


