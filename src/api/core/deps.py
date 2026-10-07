from typing import Annotated

from fastapi import Depends, Request, WebSocket

from src.api.core.config import Settings
from src.api.core.pg import PgClient
from src.services.connection_manager import ConnectionManager
from src.services.game_repo import GameRepo


def get_pg(request: Request):
    return request.app.state.pg


def get_settings(request: Request):
    return request.app.state.settings


def get_connection_manager(request: WebSocket):
    return request.app.state.connection_manager


def get_settings_ws(websocket: WebSocket):
    return websocket.app.state.settings


def get_game_repo_ws(websocket: WebSocket):
    return websocket.app.state.game_repo


PG = Annotated[PgClient, Depends(get_pg)]
SETTINGS = Annotated[Settings, Depends(get_settings)]
CONNECTION_MANAGER = Annotated[ConnectionManager, Depends(get_connection_manager)]
SETTINGS_WS = Annotated[Settings, Depends(get_settings_ws)]
GAME_REPO_WS = Annotated[GameRepo, Depends(get_game_repo_ws)]
