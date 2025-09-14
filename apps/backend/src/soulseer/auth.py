from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt
from typing import Dict, Any
from .config import settings

bearer = HTTPBearer(auto_error=False)

_jwks_cache: Dict[str, Any] | None = None

async def get_jwks() -> Dict[str, Any]:
    global _jwks_cache
    if _jwks_cache is None:
        url = settings.clerk_jwks_url or "https://clerk.dev/.well-known/jwks.json"
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url)
            res.raise_for_status()
            _jwks_cache = res.json()
    return _jwks_cache

async def get_current_user_token(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Dict[str, Any]:
    if not creds or creds.scheme.lower() != 'bearer':
        raise HTTPException(status_code=401, detail="Missing token")
    token = creds.credentials
    jwks = await get_jwks()
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token")
        payload = jwt.decode(token, key, algorithms=[key["alg"]], audience=None, options={"verify_aud": False})
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")