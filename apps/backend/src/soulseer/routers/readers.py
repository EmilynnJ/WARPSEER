from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token

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

@router.get("/me/balance")
async def my_balance(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    rb = db.query(models.ReaderBalance).filter(models.ReaderBalance.user_id == user.id).one_or_none()
    if not rb:
        rb = models.ReaderBalance(user_id=user.id, balance_cents=0)
        db.add(rb)
        db.commit()
        db.refresh(rb)
    sa = db.query(models.StripeAccount).filter(models.StripeAccount.user_id == user.id).one_or_none()
    return {
        "balance_cents": rb.balance_cents,
        "stripe": {
            "connected": bool(sa and sa.details_submitted),
            "account_id": sa.account_id if sa else None
        }
    }

@router.get("/me/ledger")
async def my_ledger(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    rows = (
        db.query(models.ReaderLedgerEntry)
        .filter(models.ReaderLedgerEntry.reader_id == user.id)
        .order_by(models.ReaderLedgerEntry.created_at.desc())
        .limit(50)
        .all()
    )
    items = [
        {
            "kind": r.kind,
            "amount_cents": r.amount_cents,
            "ref_type": r.ref_type,
            "ref_id": r.ref_id,
            "created_at": r.created_at,
        }
        for r in rows
    ]
    return {"items": items}
