from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token
from ..config import settings
import stripe

router = APIRouter(prefix="/connect", tags=["connect"])
stripe.api_key = settings.stripe_secret_key

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/onboard_link')
async def create_onboard_link(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    # Reader only
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    if user.role != 'reader':
        raise HTTPException(403, 'Only readers can onboard payouts')
    acc = db.query(models.StripeAccount).filter(models.StripeAccount.user_id == user.id).one_or_none()
    if not acc:
        account = stripe.Account.create(type='express', country='US', email=user.email, business_type='individual')
        acc = models.StripeAccount(user_id=user.id, account_id=account['id'], details_submitted=account['details_submitted'])
        db.add(acc)
        db.commit()
        db.refresh(acc)
    link = stripe.AccountLink.create(
        account=acc.account_id,
        refresh_url=(settings.frontend_public_url or 'http://localhost:5173') + '/dashboard/reader/payouts',
        return_url=(settings.frontend_public_url or 'http://localhost:5173') + '/dashboard/reader/payouts',
        type='account_onboarding'
    )
    return {"url": link['url']}