import uvicorn

from src.api.app_factory import create_app
from src.api.core.config import Settings
from src.api.core.deps import PG

settings = Settings()

app = create_app(settings)


@app.get("/health")
async def health(pg: PG):
    res = await pg.fetchval("select 1")
    if not res or res != 1:
        return {"status": "Not ok"}
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
