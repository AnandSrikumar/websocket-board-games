import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.app_factory import create_app
from src.api.core.config import Settings
from src.api.core.pg import PgClient
from src.api.core.security import hash_password


SCHEMA_FILE = "migrations/db_schema.sql"

@pytest_asyncio.fixture(scope="session")
async def settings():
    return Settings(_env_file=".env-test")




async def ensure_database_exists(settings):
    admin_dsn = (
        f"postgresql://{settings.postgres_user}:"
        f"{settings.postgres_password}@"
        f"{settings.postgres_host}:"
        f"{settings.postgres_port}/postgres"
    )

    conn = await asyncpg.connect(admin_dsn)

    try:
        exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_database
                WHERE datname = $1
            )
            """,
            settings.postgres_db,
        )

        if not exists:
            await conn.execute(
                f'CREATE DATABASE "{settings.postgres_db}"'
            )

    finally:
        await conn.close()

async def initialize_schema(settings: Settings):
    schema = open(SCHEMA_FILE, encoding="utf-8").read()

    conn = await asyncpg.connect(settings.postgres_dsn)

    try:
        await conn.execute(schema)
    finally:
        await conn.close()
        
@pytest_asyncio.fixture(scope="session")
async def database(settings):
    await drop_database(settings)
    await ensure_database_exists(settings)    
    await initialize_schema(settings)

async def drop_database(settings):
    admin_dsn = (
            f"postgresql://{settings.postgres_user}:"
            f"{settings.postgres_password}@"
            f"{settings.postgres_host}:"
            f"{settings.postgres_port}/postgres"
        )
    
    conn = await asyncpg.connect(admin_dsn)
    try:
        await conn.execute('drop database if exists "websocket-games-test"')
    finally:
        await conn.close()


@pytest_asyncio.fixture
async def app(settings, database):
    app = create_app(settings)

    async with app.router.lifespan_context(app):
        yield app    


@pytest_asyncio.fixture
async def pg(app):
    return app.state.pg


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test/v1/",
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def seed_database(pg):
    # user
    await pg.execute(
        """
        INSERT INTO users (
            username,
            email,
            password_hash
        )
        VALUES
            ($1, $2, $3),
            ($4, $5, $6)
        ON CONFLICT DO NOTHING
        """,
        "testuser1",
        "test1@example.com",
        hash_password("Password@123"),
        "testuser2",
        "test2@example.com",
        hash_password("Password@123"),
    )
