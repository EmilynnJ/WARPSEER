from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token

router = APIRouter(prefix="/notifications", tags=["notifications"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def list_notifications(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    notifs = db.query(models.Notification).filter(
        models.Notification.user_id == user.id
    ).order_by(models.Notification.created_at.desc()).limit(50).all()
    
    return {
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "type": n.type,
                "read": n.read,
                "created_at": n.created_at
            }
            for n in notifs
        ]
    }

@router.post("/{notif_id}/read")
async def mark_read(notif_id: int, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    notif = db.query(models.Notification).filter(
        models.Notification.id == notif_id,
        models.Notification.user_id == user.id
    ).one_or_none()
    
    if not notif:
        raise HTTPException(404, "Notification not found")
    
    notif.read = True
    db.commit()
    return {"ok": True}

@router.post("/subscribe")
async def subscribe_push(payload: dict, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    player_id = payload.get('player_id')
    device_type = payload.get('device_type', 'web')
    
    if not player_id:
        raise HTTPException(400, "player_id required")
    
    # Check if already exists
    existing = db.query(models.PushSubscription).filter(
        models.PushSubscription.player_id == player_id
    ).one_or_none()
    
    if existing:
        existing.user_id = user.id
        existing.active = True
    else:
        sub = models.PushSubscription(
            user_id=user.id,
            player_id=player_id,
            device_type=device_type
        )
        db.add(sub)
    
    db.commit()
    return {"ok": True}