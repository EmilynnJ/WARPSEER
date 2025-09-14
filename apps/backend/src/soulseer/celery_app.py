from celery import Celery
from .config import settings
from .db import SessionLocal
from . import models
from sqlalchemy.orm import Session
from .services.billing import bill_one_minute
from redis import Redis

celery = Celery(
    'soulseer',
    broker=settings.redis_url,
    backend=settings.redis_url
)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily payouts at 2am UTC
    sender.add_periodic_task(24*60*60, run_daily_payouts.s(), name='daily_payouts')
    # Billing tick every minute
    sender.add_periodic_task(60.0, billing_tick.s(), name='billing_tick')

@celery.task
def run_daily_payouts():
    # Implement Stripe Connect transfers to readers with balance > $15
    import stripe
    from datetime import datetime
    stripe.api_key = settings.stripe_secret_key
    db: Session = SessionLocal()
    try:
        # join balances and stripe accounts
        rows = (
            db.query(models.ReaderBalance, models.StripeAccount)
            .join(models.StripeAccount, models.StripeAccount.user_id == models.ReaderBalance.user_id)
            .filter(models.ReaderBalance.balance_cents > 1500, models.StripeAccount.details_submitted == True)
            .all()
        )
        for rb, sa in rows:
            amount = int(rb.balance_cents)
            if amount <= 0:
                continue
            idempotency_key = f"payout:{rb.user_id}:{datetime.utcnow().strftime('%Y%m%d')}:{amount}"
            try:
                stripe.Transfer.create(
                    amount=amount,
                    currency='usd',
                    destination=sa.account_id,
                    description='SoulSeer daily payout',
                    idempotency_key=idempotency_key,
                )
            except Exception:
                # skip on failure
                continue
            # record ledger and zero out balance
            db.add(models.ReaderLedgerEntry(reader_id=rb.user_id, kind='payout', amount_cents=amount, ref_type='transfer', ref_id=idempotency_key))
            rb.balance_cents = 0
            db.add(rb)
        db.commit()
    finally:
        db.close()
    return True

@celery.task
def billing_tick():
    r = Redis.from_url(settings.redis_url, decode_responses=True)
    db: Session = SessionLocal()
    try:
        # Find active sessions
        sessions = db.query(models.Session).filter(models.Session.status == 'active').all()
        for s in sessions:
            # Presence check: both client and reader seen recently
            p_client = r.get(f'session:{s.session_uid}:user:{s.client_id}')
            p_reader = r.get(f'session:{s.session_uid}:user:{s.reader_id}')
            if not (p_client and p_reader):
                continue
            # Determine per-minute rate
            rp = db.query(models.ReaderProfile).filter(models.ReaderProfile.user_id == s.reader_id).one_or_none()
            if not rp:
                continue
            if s.mode == 'chat':
                rate = rp.rate_chat_ppm
            elif s.mode == 'voice':
                rate = rp.rate_voice_ppm
            else:
                rate = rp.rate_video_ppm
            ok = bill_one_minute(db, s, rate)
            if not ok:
                # End session
                s.status = 'ended'
                db.add(s)
        db.commit()
    finally:
        db.close()
    return True

from celery import Celery
from .config import settings

celery = Celery(
    'soulseer',
    broker=settings.redis_url,
    backend=settings.redis_url
)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily payouts at 2am UTC
    sender.add_periodic_task(24*60*60, run_daily_payouts.s(), name='daily_payouts')
    # Billing tick every minute
    sender.add_periodic_task(60.0, billing_tick.s(), name='billing_tick')

@celery.task
def run_daily_payouts():
    # TODO: Implement Stripe Connect transfers to readers with balance > $15
    return True