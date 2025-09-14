from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token
from datetime import datetime
import secrets

router = APIRouter(prefix="/sessions", tags=["sessions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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