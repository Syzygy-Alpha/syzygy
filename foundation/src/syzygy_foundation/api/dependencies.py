from typing import Annotated, cast

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from syzygy_foundation.auth.security import AuthenticatedUser, decode_access_token
from syzygy_foundation.config import Settings

bearer_scheme = HTTPBearer(auto_error=False)


def settings_from_request(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(settings_from_request)],
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
        )
    try:
        return decode_access_token(credentials.credentials, settings)
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid bearer token",
        ) from exc
