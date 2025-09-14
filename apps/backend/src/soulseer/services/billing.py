from sqlalchemy.orm import Session
from .. import models
from ..services.wallet import debit
from ..config import settings

READER_SHARE = settings.reader_share_pct  # percent
PLATFORM_SHARE = 100 - READER_SHARE


def get_or_create_reader_balance(db: Session, reader_id: int) -> models.ReaderBalance:
    rb = db.query(models.ReaderBalance).filter(models.ReaderBalance.user_id == reader_id).one_or_none()
    if not rb:
        rb = models.ReaderBalance(user_id=reader_id, balance_cents=0)
        db.add(rb)
        db.flush()
    return rb


def credit_reader(db: Session, reader_id: int, amount_cents: int, ref_type: str, ref_id: str):
    rb = get_or_create_reader_balance(db, reader_id)
    rb.balance_cents += amount_cents
    db.add(models.ReaderLedgerEntry(reader_id=reader_id, kind='credit', amount_cents=amount_cents, ref_type=ref_type, ref_id=ref_id))


def bill_one_minute(db: Session, sess: models.Session, rate_cents: int):
    """Debit client balance and split to reader/platform. Returns True if billed, False if insufficient funds."""
    try:
        debit(db, sess.client_id, rate_cents, ref_type='session', ref_id=sess.session_uid)
    except Exception:
        return False
    # reader share
    reader_amount = rate_cents * READER_SHARE // 100
    credit_reader(db, sess.reader_id, reader_amount, ref_type='session', ref_id=sess.session_uid)
    # accumulate on session
    sess.total_seconds += 60
    sess.amount_charged_cents += rate_cents
    db.add(sess)
    return True