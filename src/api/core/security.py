from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(
    user_id: str,
    secret: str,
    expire_mins: int,
) -> str:

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=expire_mins),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
    )
