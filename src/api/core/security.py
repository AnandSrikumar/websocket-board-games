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


def decode_access_token(
    token: str,
    secret: str,
) -> str:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Access token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid access token")

    user_id = payload.get("sub")

    if not user_id:
        raise ValueError("Invalid access token: missing subject")

    return user_id
