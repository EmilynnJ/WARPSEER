from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me")
async def me(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    clerk_user_id = token.get("sub")
    if not clerk_user_id:
        raise HTTPException(401, "Invalid token")
    user = db.query(models.User).filter(models.User.clerk_user_id == clerk_user_id).one_or_none()
    if not user:
        # Auto-provision client account
        user = models.User(clerk_user_id=clerk_user_id, email=token.get("email", ""), role="client", display_name=token.get("first_name", "") or token.get("username", ""))
        db.add(user)
        db.commit()
        db.refresh(user)
    return {"id": user.id, "role": user.role, "email": user.email, "display_name": user.display_name}