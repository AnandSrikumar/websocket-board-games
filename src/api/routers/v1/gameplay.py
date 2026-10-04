from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
    APIRouter,
)

from src.api.core.deps import CONNECTION_MANAGER, SETTINGS, SETTINGS_WS
from src.services.auth_validations import authenticate_websocket
from src.log import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/play")


@router.websocket("/join")
async def game_join(
    websocket: WebSocket, token: str, manager: CONNECTION_MANAGER, settings: SETTINGS_WS
):
    user_id = await authenticate_websocket(token, settings.jwt_secret)
    log.info("Websocket authenticated....")
    is_connected = await manager.connect(user_id, websocket)
    if not is_connected:
        await websocket.close(code=1008, reason=f"User already connected")
        return
    log.info(
        f"user: {user_id} connected. Total Connections: {manager.connection_count}"
    )

    try:
        while True:
            message = await websocket.receive_text()
            log.info(f"User: {user_id} -> {message}")
            await websocket.send_text(f"ECHO: {message}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        log.info(f"User: {user_id} disconnected")
