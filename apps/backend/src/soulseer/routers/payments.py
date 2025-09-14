from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token
from ..config import settings
from ..services.wallet import credit
import stripe

stripe.api_key = settings.stripe_secret_key

router = APIRouter(prefix="/payments", tags=["payments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/topup/intents")
async def create_topup_intent(payload: dict, token=Depends(get_current_user_token)):
    # Create a PaymentIntent for client wallet top-up
    amount_cents = int(payload.get("amount_cents", 0))
    if amount_cents < 100:
        raise HTTPException(400, "Minimum top-up is $1.00")
    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        automatic_payment_methods={"enabled": True},
        metadata={"purpose": "wallet_topup", "clerk_user_id": token.get("sub")},
    )
    return {"client_secret": intent["client_secret"], "payment_intent_id": intent["id"]}

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_signing_secret)
    except Exception as e:
        raise HTTPException(400, f"Webhook error: {e}")

    if event["type"] == "payment_intent.succeeded":
        pi = event["data"]["object"]
        amount = int(pi["amount"])  # cents
        clerk_user_id = pi["metadata"].get("clerk_user_id") if pi.get("metadata") else None
        if clerk_user_id:
            db = SessionLocal()
            try:
                user = db.query(models.User).filter(models.User.clerk_user_id == clerk_user_id).one_or_none()
                if user:
                    credit(db, user.id, amount, ref_type="payment_intent", ref_id=pi["id"])
                    db.commit()
            finally:
                db.close()
    return {"received": True}