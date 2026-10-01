from fastapi import APIRouter, HTTPException

from src.api.core.deps import PG, SETTINGS
from src.api.core.security import (create_access_token, hash_password,
                                   verify_password)
from src.api.models.auth import Login, LoginSuccess, Register, RegisterSuccess

router = APIRouter(prefix="/auth")

INSERT_USER_QUERY = """
insert into users(username, email, password_hash) values ($1, $2,$3) returning id, username
"""

LOGIN_ENDPOINT = """
select id, username, password_hash from users where lower(username)=lower($1) or lower(email)=lower($1)
"""


@router.post("/register")
async def register(body: Register, pg: PG) -> RegisterSuccess:
    password_hash = hash_password(body.password)
    insert_result = await pg.fetchrow(
        INSERT_USER_QUERY, body.username, body.email, password_hash
    )
    return {"id": insert_result["id"], "username": insert_result["username"]}


@router.post("/login")
async def login(body: Login, pg: PG, settings: SETTINGS) -> LoginSuccess:
    user = await pg.fetchrow(LOGIN_ENDPOINT, body.identifier)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(
        user_id=str(user["id"]),
        secret=settings.jwt_secret,
        expire_mins=settings.jwt_exp_mins,
    )

    return {"access_token": access_token, "token_type": "bearer"}
