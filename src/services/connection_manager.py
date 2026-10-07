import asyncio
from dataclasses import dataclass
from uuid import UUID
import uuid

from fastapi import WebSocket

from src.exceptions import PlayerNotConnectedError
from src.services.game_repo import GameRepo
from src.services.series_manager import SeriesManager

from src.log import get_logger
log = get_logger(__name__)


@dataclass
class PlayerSession:
    player_id: UUID
    websocket: WebSocket
    game_id: UUID
    target_wins: int = 10
    connected: bool = True


class ConnectionManager:
    def __init__(self, game_repo: GameRepo):
        self._waiting_queue: dict[UUID, asyncio.Queue[UUID]] = {}
        self._connections: dict[UUID, PlayerSession] = {}
        self._workers: dict[UUID, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._game_repo = game_repo
        self._series = []

    async def connect(
        self,
        player_id: UUID,
        websocket: WebSocket,
        game_id: UUID,
        target_wins: int = 10,
    ) -> tuple[bool, str]:
        try:
            async with self._lock:
                if player_id in self._connections:
                    return False, "Player already in waiting queue or game"
                player_session = PlayerSession(player_id, websocket, game_id, target_wins)
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

    async def _run(self, game_id: UUID):
        queue = self._waiting_queue[game_id]
        while True:
            player1 = await queue.get()
            player2 = await queue.get()
            target_wins = self._connections[player1].target_wins
            try:
                series_id = await self._game_repo.create_series(
                    player1, player2, target_wins, game_id
                )
                self._series.append(
                    SeriesManager(series_id, player1, player2, target_wins, game_id)
                )
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
