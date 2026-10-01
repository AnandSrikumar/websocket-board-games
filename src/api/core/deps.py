from typing import Annotated

from fastapi import Depends, Request

from src.api.core.config import Settings
from src.api.core.pg import PgClient


def get_pg(request: Request):
    return request.app.state.pg


def get_settings(request: Request):
    return request.app.state.settings


PG = Annotated[PgClient, Depends(get_pg)]
SETTINGS = Annotated[Settings, Depends(get_settings)]
