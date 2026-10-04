import asyncio

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        async with self._lock:
            if user_id in self.connections:
                return False
            self.connections[user_id] = websocket
        await websocket.accept()
        return True

    def disconnect(self, user_id: int):
        self.connections.pop(user_id, None)

    @property
    def connection_count(self) -> int:
        return len(self.connections)
