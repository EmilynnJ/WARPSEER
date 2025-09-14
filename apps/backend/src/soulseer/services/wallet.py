from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import models

def get_or_create_wallet(db: Session, user_id: int) -> models.Wallet:
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user_id).one_or_none()
    if not wallet:
        wallet = models.Wallet(user_id=user_id, balance_cents=0)
        db.add(wallet)
        db.flush()
    return wallet

def credit(db: Session, user_id: int, amount_cents: int, ref_type: str, ref_id: str):
    if amount_cents <= 0:
        raise HTTPException(400, "amount must be positive")
    wallet = get_or_create_wallet(db, user_id)
    wallet.balance_cents += amount_cents
    db.add(models.LedgerEntry(user_id=user_id, kind="credit", amount_cents=amount_cents, ref_type=ref_type, ref_id=ref_id))

def debit(db: Session, user_id: int, amount_cents: int, ref_type: str, ref_id: str):
    if amount_cents <= 0:
        raise HTTPException(400, "amount must be positive")
    wallet = get_or_create_wallet(db, user_id)
    if wallet.balance_cents < amount_cents:
        raise HTTPException(402, "Insufficient balance")
    wallet.balance_cents -= amount_cents
    db.add(models.LedgerEntry(user_id=user_id, kind="debit", amount_cents=amount_cents, ref_type=ref_type, ref_id=ref_id))