from fastapi import APIRouter

from src.api.routers.v1.auth import router as auth_router

def v1_routers():
    router = APIRouter(prefix='/v1')
    router.include_router(auth_router)
    return router