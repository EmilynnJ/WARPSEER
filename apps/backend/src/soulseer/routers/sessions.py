from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token
from datetime import datetime
from fastapi import Request
from ..config import settings
from redis import Redis
import secrets

router = APIRouter(prefix="/sessions", tags=["sessions"]) 

redis_client: Redis | None = None

def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/incoming")
async def incoming(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    # For reader: list requested sessions
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get("sub")).one()
    q = db.query(models.Session).filter(models.Session.reader_id == user.id, models.Session.status == 'requested')
    items = [{"session_uid": s.session_uid, "mode": s.mode, "client_id": s.client_id} for s in q.all()]
    return {"items": items}

@router.get("/{session_uid}")
async def get_session(session_uid: str, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    sess = db.query(models.Session).filter(models.Session.session_uid == session_uid).one_or_none()
    if not sess:
        raise HTTPException(404, "Not found")
    return {
        "session_uid": sess.session_uid,
        "status": sess.status,
        "mode": sess.mode,
        "started_at": sess.started_at,
        "ended_at": sess.ended_at,
        "total_seconds": sess.total_seconds,
        "amount_charged_cents": sess.amount_charged_cents
    }

@router.post("/request")
async def request_session(payload: dict, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    reader_id = int(payload.get("reader_id"))
    mode = payload.get("mode")
    if mode not in {"chat","voice","video"}:
        raise HTTPException(400, "Invalid mode")
    client_user = db.query(models.User).filter(models.User.clerk_user_id == token.get("sub")).one()
    session = models.Session(
        session_uid=secrets.token_urlsafe(12),
        reader_id=reader_id,
        client_id=client_user.id,
        mode=mode,
        status="requested"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    # Notify reader via Redis channel
    r = get_redis()
    r.publish(f"user_notify:{reader_id}", f"new_session:{session.session_uid}")
    return {"session_uid": session.session_uid, "status": session.status}

@router.post("/{session_uid}/accept")
async def accept_session(session_uid: str, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    # Reader accepts
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get("sub")).one()
    sess = db.query(models.Session).filter(models.Session.session_uid == session_uid).one_or_none()
    if not sess:
        raise HTTPException(404, "Not found")
    if user.role != "reader" or user.id != sess.reader_id:
        raise HTTPException(403, "Only assigned reader can accept")
    sess.status = "active"
    sess.started_at = datetime.utcnow()
    db.add(sess)
    db.commit()
    return {"ok": True}

@router.post("/{session_uid}/reject")
async def reject_session(session_uid: str, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get("sub")).one()
    sess = db.query(models.Session).filter(models.Session.session_uid == session_uid).one_or_none()
    if not sess:
        raise HTTPException(404, "Not found")
    if user.role != "reader" or user.id != sess.reader_id:
        raise HTTPException(403, "Only assigned reader can reject")
    if sess.status != 'requested':
        raise HTTPException(400, "Only requested sessions can be rejected")
    sess.status = "canceled"
    sess.ended_at = datetime.utcnow()
    db.add(sess)
    db.commit()
    return {"ok": True}

@router.post("/{session_uid}/end")
async def end_session(session_uid: str, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    # Either party can end
    sess = db.query(models.Session).filter(models.Session.session_uid == session_uid).one_or_none()
    if not sess:
        raise HTTPException(404, "Not found")
    sess.status = "ended"
    sess.ended_at = datetime.utcnow()
    db.add(sess)
    db.commit()
    return {"ok": True}