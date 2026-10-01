from contextlib import asynccontextmanager
from typing import Any

import asyncpg

from src.log import get_logger

log = get_logger(__name__)


class PgClient:
    def __init__(self, dsn: str, max_size: int):
        self._dsn = dsn
        self._pool = None
        self._max_size = max_size

    async def create(self):
        if self._pool is not None:
            raise RuntimeError("Pg client already initialized")
        self._pool = await asyncpg.create_pool(self._dsn, max_size=self._max_size)
        log.info(f"PG client created successfully....")

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def execute(
        self,
        query: str,
        *args: Any,
    ) -> str:
        pool = self._pool
        log.debug(f"executing: {query} with {args}")
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(
        self,
        query: str,
        *args: Any,
    ) -> list[asyncpg.Record]:
        pool = self._pool
        log.debug(f"Fetching query: {query} with {args}")
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(
        self,
        query: str,
        *args: Any,
    ) -> asyncpg.Record | None:
        pool = self._pool
        log.debug(f"Fetching query for row: {query} with {args}")
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(
        self,
        query: str,
        *args: Any,
    ) -> Any:
        pool = self._pool
        async with pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    @asynccontextmanager
    async def transaction(self):
        pool = self._pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                yield conn
