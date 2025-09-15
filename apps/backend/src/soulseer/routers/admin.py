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

@router.get("/stats")
async def admin_stats(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    _ensure_admin(token)
    
    # Get counts
    total_users = db.query(models.User).count()
    total_readers = db.query(models.User).filter(models.User.role == 'reader').count()
    total_sessions = db.query(models.Session).count()
    total_appointments = db.query(models.Appointment).count()
    total_orders = db.query(models.Order).count()
    
    # Revenue
    total_revenue = db.query(models.LedgerEntry).filter(
        models.LedgerEntry.kind == 'credit',
        models.LedgerEntry.ref_type == 'payment_intent'
    ).count()
    
    return {
        "users": total_users,
        "readers": total_readers,
        "sessions": total_sessions,
        "appointments": total_appointments,
        "orders": total_orders,
        "revenue_transactions": total_revenue
    }

@router.get("/users")
async def list_users(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    _ensure_admin(token)
    users = db.query(models.User).limit(100).all()
    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "display_name": u.display_name,
                "created_at": u.created_at
            }
            for u in users
        ]
    }

@router.post("/users/{user_id}/role")
async def update_role(user_id: int, payload: dict, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    _ensure_admin(token)
    user = db.query(models.User).filter(models.User.id == user_id).one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    
    new_role = payload.get('role')
    if new_role not in ['client', 'reader', 'admin']:
        raise HTTPException(400, "Invalid role")
    
    user.role = new_role
    db.commit()
    return {"ok": True}
