from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any
import json
from ..config import settings

router = APIRouter(prefix="/signaling", tags=["signaling"])

# In-memory connections per session (prod: use Redis pubsub or connection manager)
session_peers: Dict[str, set[WebSocket]] = {}

@router.websocket("/ws/{session_uid}")
async def websocket_endpoint(ws: WebSocket, session_uid: str):
    await ws.accept()
    peers = session_peers.setdefault(session_uid, set())
    peers.add(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
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