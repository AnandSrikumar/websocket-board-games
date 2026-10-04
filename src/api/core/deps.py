from typing import Annotated

from fastapi import Depends, Request, WebSocket

from src.api.core.config import Settings
from src.api.core.pg import PgClient
from src.services.connection_manager import ConnectionManager


def get_pg(request: Request):
    return request.app.state.pg


def get_settings(request: Request):
    return request.app.state.settings


def get_connection_manager(request: WebSocket):
    return request.app.state.connection_manager


def get_settings_ws(websocket: WebSocket):
    return websocket.app.state.settings


PG = Annotated[PgClient, Depends(get_pg)]
SETTINGS = Annotated[Settings, Depends(get_settings)]
CONNECTION_MANAGER = Annotated[ConnectionManager, Depends(get_connection_manager)]
SETTINGS_WS = Annotated[Settings, Depends(get_settings_ws)]
