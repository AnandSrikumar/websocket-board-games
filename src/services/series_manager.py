from dataclasses import asdict
from uuid import UUID

from src.games.game_factory import get_game
from src.games.game import GameBase
from src.log import get_logger
from src.services.game_repo import GameRepo
from src.services.player_models import PlayerSession

log = get_logger(__name__)


class SeriesManager:
    def __init__(
        self,
        player_sessions: dict[UUID, PlayerSession],
        series_id: UUID,
        game_repo: GameRepo,
    ):
        self._player_sessions = player_sessions
        self._series_id = series_id
        self._wins: dict[UUID, int] = {}
        self._is_game_started = False
        self._is_series_done = False
        self._repo = game_repo
        self._game_object: GameBase | None = None

    async def _create_match(self):
        game = None
        for _, session in self._player_sessions.items():
            game = session.game_name
            break
        match_id = await self._repo.create_match(self._series_id)
        self._game_object = get_game(game, match_id)
        for _, session in self._player_sessions.items():
            self._game_object.add_player(session.player_name)

    async def make_move(self, player_id: UUID, payload: dict):
        if not self._is_game_started:
            await self._create_match()
        player_name = self._player_sessions[player_id].player_name
        move_res = self._game_object.make_move(player_name, payload)
        log.info(f"player: {player_id} -> {asdict(move_res)}")
