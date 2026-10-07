from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI

from src.api.routers.routers import v1_routers
from src.api.core.config import Settings
from src.api.core.exceptions import handle_postgres_error
from src.api.core.pg import PgClient
from src.log import get_logger, setup_logging
from src.services.connection_manager import ConnectionManager
from src.services.game_repo import GameRepo


def create_app(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        pg = PgClient(settings.postgres_dsn, settings.postgres_max_pool)
        try:
            await pg.create()
            app.state.pg = pg
            log.info(f"Postgres attached to the app")
            game_repo = GameRepo(pg)
            app.state.connection_manager = ConnectionManager(game_repo)
            app.state.game_repo = game_repo
            log.info(f"Game repo and connection manager created...")
            yield
        except Exception as e:
            log.error(f"app factory failed: {e}")
            raise
        finally:
            await pg.close()
            log.info(f"Postgres closed")
            await app.state.connection_manager.shutdown()
            log.info(f"Connection manager shut down....")

    setup_logging()
    log = get_logger(__name__)
    app = FastAPI(lifespan=lifespan, description="Websocket games")
    app.add_exception_handler(asyncpg.PostgresError, handle_postgres_error)
    app.include_router(v1_routers())
    return app
