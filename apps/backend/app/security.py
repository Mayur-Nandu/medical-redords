from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt, JWTError
from pydantic import BaseModel
from time import time

from .config import get_settings


class TokenPayload(BaseModel):
    sub: str | None = None
    realm_access: dict | None = None
    resource_access: dict | None = None
    preferred_username: str | None = None


bearer_scheme = HTTPBearer(auto_error=False)

_jwks_cache: dict[str, tuple[dict, float]] = {}
_JWKS_TTL_SECONDS = 600


async def _fetch_jwks(realm_issuer: str) -> dict:
    cached = _jwks_cache.get(realm_issuer)
    now = time()
    if cached and now - cached[1] < _JWKS_TTL_SECONDS:
        return cached[0]

    url = f"{realm_issuer}/protocol/openid-connect/certs"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        jwks = resp.json()
        _jwks_cache[realm_issuer] = (jwks, now)
        return jwks


def _get_key_from_jwks(jwks: dict, kid: str | None) -> dict | None:
    if not kid:
        return None
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> TokenPayload:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    settings = get_settings()
    token = creds.credentials
    try:
        headers = jwt.get_unverified_header(token)
        issuer = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
        jwks = await _fetch_jwks(f"{settings.keycloak_url}/realms/{settings.keycloak_realm}")
        key = _get_key_from_jwks(jwks, headers.get("kid"))
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signing key not found")
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_aud": False},
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OIDC provider unavailable")

    return TokenPayload(**payload)


def require_role(required_role: str):
    async def dependency(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        roles: list[str] = []
        if user.realm_access and isinstance(user.realm_access.get("roles"), list):
            roles.extend(user.realm_access["roles"])  # type: ignore
        if required_role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency

