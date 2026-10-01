import asyncio
from pathlib import Path

import asyncpg
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent
SQL_FILE = BASE_DIR / "migrations/db_schema.sql"

def get_db_url() -> str:
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    database = os.environ["POSTGRES_DB"]
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

async def create_schema():
    load_dotenv()

    database_url = get_db_url()

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    sql = SQL_FILE.read_text(encoding="utf-8")

    conn = await asyncpg.connect(database_url)

    try:
        await conn.execute(sql)
        print("Database schema created successfully.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(create_schema())