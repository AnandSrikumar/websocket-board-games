from uuid import UUID

from src.api.core.pg import PgClient


class GameRepo:
    def __init__(self, pg: PgClient):
        self._pg = pg

    async def get_game_type_id(self, game: str):
        q = "select id from game where name=$1"
        res = await self._pg.fetchval(q, game)
        return res

    async def create_series(
        self, player1_id: UUID, player2_id: UUID, target_wins: int, game_id: UUID
    ):
        # game_id = await self.get_game_type_id(game)
        q = """
            Insert into series (game_id, player1_id, player2_id, target_wins) values
            ($1, $2, $3, $4) returning id
        """
        res = await self._pg.fetchrow(q, game_id, player1_id, player2_id, target_wins)
        return res["id"]
