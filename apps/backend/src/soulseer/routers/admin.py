from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token
from ..config import settings

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _ensure_admin(token):
    email = token.get("email")
    if not email or email.lower() != settings.admin_email.lower():
        raise HTTPException(403, "Admins only")

@router.post("/readers/{user_id}/promote")
async def promote_reader(user_id: int, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    _ensure_admin(token)
    user = db.query(models.User).filter(models.User.id == user_id).one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    user.role = "reader"
    db.add(user)
    # Create reader profile if missing
    rp = db.query(models.ReaderProfile).filter(models.ReaderProfile.user_id == user.id).one_or_none()
    if not rp:
        rp = models.ReaderProfile(user_id=user.id)
        db.add(rp)
    db.commit()
    return {"ok": True, "user_id": user.id, "role": user.role}