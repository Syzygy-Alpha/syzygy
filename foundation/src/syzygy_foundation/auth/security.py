from datetime import UTC, datetime, timedelta
from hmac import compare_digest
from typing import Any

import jwt
from pydantic import BaseModel

from syzygy_foundation.config import Settings


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthenticatedUser(BaseModel):
    username: str


def authenticate_user(username: str, password: str, settings: Settings) -> bool:
    expected_username = settings.admin_username
    expected_password = settings.admin_password.get_secret_value()
    return compare_digest(username, expected_username) and compare_digest(
        password,
        expected_password,
    )


def create_access_token(subject: str, settings: Settings) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expires_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at}
    return jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str, settings: Settings) -> AuthenticatedUser:
    payload = jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        msg = "token subject is missing"
        raise ValueError(msg)
    return AuthenticatedUser(username=subject)
