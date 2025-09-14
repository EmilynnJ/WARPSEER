from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt
from ..auth import get_jwks
from redis.asyncio import Redis as AsyncRedis
from ..config import settings
from ..db import SessionLocal
from .. import models
from typing import Dict, Any
import json
from ..config import settings

router = APIRouter(prefix="/signaling", tags=["signaling"]) 
aredis: AsyncRedis | None = None
async def get_async_redis():
    global aredis
    if aredis is None:
        aredis = AsyncRedis.from_url(settings.redis_url, decode_responses=True)
    return aredis

# In-memory connections per session (prod: use Redis pubsub or connection manager)
session_peers: Dict[str, set[WebSocket]] = {}

@router.websocket("/ws/{session_uid}")
async def websocket_endpoint(ws: WebSocket, session_uid: str):
    # Require JWT token passed as query parameter ?token=...
    token = ws.query_params.get('token')
    if not token:
        await ws.close(code=4401)
        return
    # Verify token
    try:
        jwks = await get_jwks()
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        payload = jwt.decode(token, key, algorithms=[key["alg"]], audience=None, options={"verify_aud": False})
        clerk_id = payload.get('sub')
        # map to numeric user id
        db = SessionLocal()
        try:
            u = db.query(models.User).filter(models.User.clerk_user_id == clerk_id).one_or_none()
            if not u:
                await ws.close(code=4401)
                return
            user_id = u.id
        finally:
            db.close()
    except Exception:
        await ws.close(code=4401)
        return
    await ws.accept()
    peers = session_peers.setdefault(session_uid, set())
    r = await get_async_redis()
    # Presence key for this user
    presence_key = f"session:{session_uid}:user:{user_id}"
    await r.set(presence_key, "1", ex=15)
    peers.add(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get('type') == 'heartbeat':
                # refresh presence
                await r.expire(presence_key, 15)
                continue
            # Broadcast to other peers in the same session
            for peer in list(peers):
                if peer is not ws:
                    try:
                        await peer.send_text(json.dumps(msg))
                    except Exception:
                        pass
    except WebSocketDisconnect:
        peers.remove(ws)
        if not peers:
            session_peers.pop(session_uid, None)
        # clear presence
        try:
            r2 = await get_async_redis()
            await r2.delete(presence_key)
        except Exception:
            pass
