from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models

router = APIRouter(prefix="/streams", tags=["streams"])

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