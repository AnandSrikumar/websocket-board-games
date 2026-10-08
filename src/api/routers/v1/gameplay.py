from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
    APIRouter,
)

from src.api.core.deps import CONNECTION_MANAGER, GAME_REPO_WS, SETTINGS, SETTINGS_WS
from src.services.auth_validations import authenticate_websocket
from src.log import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/play")


@router.websocket("/join")
async def game_join(
    websocket: WebSocket,
    token: str,
    manager: CONNECTION_MANAGER,
    settings: SETTINGS_WS,
    game_repo: GAME_REPO_WS,
    game_name: str = "tictactoe",
    target_wins: int = 10,
):
    user_id = await authenticate_websocket(token, settings.jwt_secret)
    log.info("Websocket authenticated....")
    game_id = await game_repo.get_game_type_id(game_name)
    is_connected, message = await manager.connect(
        user_id, websocket, game_id, game_name, target_wins
    )
    if not is_connected:
        log.error(f"Failed to connect: {message}")
        return
    log.info(f"Websocket connection established for: {user_id}")
    await manager.enqueue(user_id)
    try:
        while True:
            message = await websocket.receive_json()
            log.info(f"{user_id}=>: {message}")
            board = await manager.communicate(user_id, message)
            await websocket.send_json({
                "event": "board_update",
                "board": board,
            })
    except WebSocketDisconnect:
        await manager.disconnect(user_id)
        log.info(f"{user_id} disconnected...")
