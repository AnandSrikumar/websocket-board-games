from fastapi import WebSocket, WebSocketException, status

from src.api.core.security import decode_access_token
from src.log import get_logger

log = get_logger(__name__)


async def authenticate_websocket(token: str, secret: str) -> int:
    if not token:
        log.info(f"No token provided")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    user = decode_access_token(token, secret)
    if not user:
        log.info("User not authenticated..")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return user
