from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token
from datetime import datetime
import secrets
import json
from typing import Dict, Set
from redis.asyncio import Redis as AsyncRedis
from ..config import settings

router = APIRouter(prefix="/streams", tags=["streams"])

# Stream viewer connections
stream_viewers: Dict[str, Set[WebSocket]] = {}

aredis: AsyncRedis | None = None
async def get_async_redis():
    global aredis
    if aredis is None:
        aredis = AsyncRedis.from_url(settings.redis_url, decode_responses=True)
    return aredis

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
async def list_streams(db: Session = Depends(get_db)):
    q = db.query(models.Session).filter(models.Session.mode == "stream", models.Session.status == "active")
    items = [
        {
            "session_uid": s.session_uid,
            "reader_id": s.reader_id,
            "started_at": s.started_at,
            "status": s.status,
        }
        for s in q.all()
    ]
    return {"items": items}

@router.post("/start")
async def start_stream(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    if user.role != 'reader':
        raise HTTPException(403, 'Only readers can start streams')
    
    # Check if already streaming
    existing = db.query(models.Session).filter(
        models.Session.reader_id == user.id,
        models.Session.mode == 'stream',
        models.Session.status == 'active'
    ).first()
    
    if existing:
        return {"session_uid": existing.session_uid}
    
    # Create new stream session
    sess = models.Session(
        session_uid=secrets.token_urlsafe(12),
        reader_id=user.id,
        client_id=user.id,  # Self for streams
        mode='stream',
        status='active',
        started_at=datetime.utcnow(),
        per_minute=False
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return {"session_uid": sess.session_uid}

@router.get("/gifts")
async def list_gifts(db: Session = Depends(get_db)):
    gifts = db.query(models.Gift).filter(models.Gift.active == True).all()
    return {
        "items": [
            {
                "id": g.id,
                "name": g.name,
                "price_cents": g.price_cents,
                "image_url": g.image_url
            }
            for g in gifts
        ]
    }

@router.post("/{session_uid}/gift")
async def send_gift(session_uid: str, payload: dict, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    gift_id = int(payload.get('gift_id'))
    
    # Verify session exists and is a stream
    sess = db.query(models.Session).filter(
        models.Session.session_uid == session_uid,
        models.Session.mode == 'stream',
        models.Session.status == 'active'
    ).one_or_none()
    
    if not sess:
        raise HTTPException(404, 'Stream not found')
    
    # Get gift
    gift = db.query(models.Gift).filter(models.Gift.id == gift_id).one_or_none()
    if not gift:
        raise HTTPException(404, 'Gift not found')
    
    # Get sender
    sender = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    
    # Debit sender wallet
    from ..services.wallet import debit
    try:
        debit(db, sender.id, gift.price_cents, ref_type='gift', ref_id=f'stream:{session_uid}')
    except Exception:
        raise HTTPException(402, 'Insufficient balance')
    
    # Credit reader (70% share)
    from ..services.billing import credit_reader
    reader_amount = gift.price_cents * settings.reader_share_pct // 100
    credit_reader(db, sess.reader_id, reader_amount, ref_type='gift', ref_id=f'stream:{session_uid}')
    
    # Record gift
    stream_gift = models.StreamGift(
        session_id=sess.id,
        sender_id=sender.id,
        gift_id=gift.id,
        amount_cents=gift.price_cents
    )
    db.add(stream_gift)
    db.commit()
    
    # Broadcast gift event to viewers
    if session_uid in stream_viewers:
        gift_event = json.dumps({
            "type": "gift",
            "sender": sender.display_name or sender.email.split('@')[0],
            "gift_name": gift.name,
            "gift_image": gift.image_url
        })
        for ws in stream_viewers[session_uid]:
            try:
                import asyncio
                asyncio.create_task(ws.send_text(gift_event))
            except:
                pass
    
    return {"ok": True}

@router.websocket("/ws/{session_uid}")
async def stream_websocket(ws: WebSocket, session_uid: str):
    await ws.accept()
    
    # Add to viewers
    if session_uid not in stream_viewers:
        stream_viewers[session_uid] = set()
    stream_viewers[session_uid].add(ws)
    
    # Send current viewer count
    viewer_count = len(stream_viewers[session_uid])
    await ws.send_text(json.dumps({"type": "viewers", "count": viewer_count}))
    
    # Broadcast viewer count to all
    for viewer in stream_viewers[session_uid]:
        try:
            await viewer.send_text(json.dumps({"type": "viewers", "count": viewer_count}))
        except:
            pass
    
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            
            # Broadcast chat messages
            if msg.get('type') == 'chat':
                for viewer in stream_viewers[session_uid]:
                    if viewer != ws:
                        try:
                            await viewer.send_text(json.dumps(msg))
                        except:
                            pass
    except WebSocketDisconnect:
        stream_viewers[session_uid].remove(ws)
        if not stream_viewers[session_uid]:
            del stream_viewers[session_uid]
        else:
            # Update viewer count
            viewer_count = len(stream_viewers[session_uid])
            for viewer in stream_viewers[session_uid]:
                try:
                    await viewer.send_text(json.dumps({"type": "viewers", "count": viewer_count}))
                except:
                    pass
