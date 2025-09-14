from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models

router = APIRouter(prefix="/readers", tags=["readers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
async def list_readers(db: Session = Depends(get_db)):
    q = (
        db.query(models.ReaderProfile, models.User)
        .join(models.User, models.User.id == models.ReaderProfile.user_id)
    )
    items = []
    for rp, u in q.all():
        items.append({
            "user_id": u.id,
            "display_name": u.display_name or u.email.split('@')[0],
            "avatar_url": rp.avatar_url,
            "rate_chat_ppm": rp.rate_chat_ppm,
            "rate_voice_ppm": rp.rate_voice_ppm,
            "rate_video_ppm": rp.rate_video_ppm,
            "status": rp.status,
        })
    return {"items": items}