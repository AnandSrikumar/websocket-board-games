import asyncio
from dataclasses import dataclass
from uuid import UUID
import uuid

from fastapi import WebSocket

from src.exceptions import PlayerNotConnectedError
from src.services.game_repo import GameRepo
from src.services.player_models import PlayerSession
from src.services.series_manager import SeriesManager

from src.log import get_logger

log = get_logger(__name__)


class ConnectionManager:
    def __init__(self, game_repo: GameRepo):
        self._waiting_queue: dict[UUID, asyncio.Queue[UUID]] = {}
        self._connections: dict[UUID, PlayerSession] = {}
        self._workers: dict[UUID, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._game_repo = game_repo
        self._series: dict[UUID, SeriesManager] = {}

    async def connect(
        self,
        player_id: UUID,
        websocket: WebSocket,
        game_id: UUID,
        game_name: str,
        target_wins: int = 10,
    ) -> tuple[bool, str]:
        try:
            player_name = await self._game_repo.get_player_name(player_id)
            async with self._lock:
                if (
                    player_id in self._connections
                    and self._connections[player_id].connected
                ):
                    return (
                        False,
                        f"Player: {player_name} already in waiting queue or game",
                    )
                player_session = PlayerSession(
                    player_id,
                    websocket,
                    game_id,
                    game_name,
                    player_name,
                    target_wins,
                )
                self._connections[player_id] = player_session
            await websocket.accept()
            return True, ""
        except Exception as e:
            log.error(f"Failed to create websocket connection: {e}")
            return False, str(e)

    async def enqueue(self, player_id: UUID):
        async with self._lock:
            if player_id not in self._connections:
                raise PlayerNotConnectedError(f"Player not connected...")
            session = self._connections[player_id]
            queue = self._waiting_queue.setdefault(
                session.game_id,
                asyncio.Queue(),
            )
            await queue.put(player_id)
            if session.game_id not in self._workers:
                self._workers[session.game_id] = asyncio.create_task(
                    self._run(session.game_id)
                )
            log.info(
                f"player: {session.player_name} is added to the queue. waiting for a match..."
            )

    async def _run(self, game_id: UUID):
        queue = self._waiting_queue[game_id]
        while True:
            player1 = await queue.get()
            player2 = await queue.get()
            player1_session = self._connections[player1]
            player2_session = self._connections[player2]
            target_wins = player1_session.target_wins
            game = player1_session.game_name  # only player 1 game needed
            try:
                series_id = await self._game_repo.create_series(
                    player1, player2, target_wins, game_id
                )
                series_object = SeriesManager(
                    {player1: player1_session, player2: player2_session},
                    series_id,
                    self._game_repo,
                )
                self._series[player1] = series_object
                self._series[player2] = series_object
                log.info(f"{player1} vs {player2} playing: {game_id}")
            except Exception as e:
                log.error(f"error in creating series: {e}")
            finally:
                queue.task_done()
                queue.task_done()

    async def disconnect(self, player_id: UUID):
        async with self._lock:
            session = self._connections.pop(player_id, None)

            if session is None:
                return
            session.connected = False
        try:
            await session.websocket.close()
        except Exception:
            pass

    async def communicate(self, player_id: UUID, message: dict):
        if player_id not in self._connections:
            raise PlayerNotConnectedError(
                f"Unknown player: {player_id} trying to communicate"
            )
        if player_id not in self._series:
            raise PlayerNotConnectedError(f"Player not yet in the game")
        board = await self._series[player_id].make_move(player_id, message)
        await self._series[player_id].check_results(board)

    async def shutdown(self):
        # Stop matchmaking workers
        for worker in self._workers.values():
            worker.cancel()

        await asyncio.gather(
            *self._workers.values(),
            return_exceptions=True,
        )

        # Close active WebSocket connections
        for session in self._connections.values():
            await session.websocket.close()

        self._workers.clear()
        self._waiting_queue.clear()
        self._connections.clear()
