from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from ..db import SessionLocal
from .. import models
from ..auth import get_current_user_token

router = APIRouter(prefix="/appointments", tags=["appointments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

ALLOWED_LENGTHS = {15, 30, 45, 60}


def compute_price_cents(rp: models.ReaderProfile, mode: str, length: int) -> int:
    if length not in ALLOWED_LENGTHS:
        raise HTTPException(400, "Invalid length")
    if mode == 'chat':
        base = rp.rate_scheduled_15 if length == 15 else rp.rate_scheduled_30 if length == 30 else rp.rate_scheduled_45 if length == 45 else rp.rate_scheduled_60
    elif mode in {'voice', 'video'}:
        # Use same flat pricing tiers; could be customized later
        base = rp.rate_scheduled_15 if length == 15 else rp.rate_scheduled_30 if length == 30 else rp.rate_scheduled_45 if length == 45 else rp.rate_scheduled_60
    else:
        raise HTTPException(400, "Invalid mode")
    return int(base)

@router.get("/me")
async def my_appointments(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    upcoming = db.query(models.Appointment).filter(models.Appointment.client_id == user.id, models.Appointment.status.in_(['scheduled','in_progress'])).order_by(models.Appointment.start_time).all()
    history = db.query(models.Appointment).filter(models.Appointment.client_id == user.id, models.Appointment.status.in_(['completed','canceled'])).order_by(models.Appointment.start_time.desc()).limit(50).all()
    return {
        "upcoming": [{"booking_uid": a.booking_uid, "reader_id": a.reader_id, "mode": a.mode, "start_time": a.start_time, "length_minutes": a.length_minutes, "status": a.status} for a in upcoming],
        "history": [{"booking_uid": a.booking_uid, "reader_id": a.reader_id, "mode": a.mode, "start_time": a.start_time, "length_minutes": a.length_minutes, "status": a.status} for a in history]
    }

@router.get("/reader")
async def reader_appointments(token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    if user.role != 'reader':
        raise HTTPException(403, 'Readers only')
    upcoming = db.query(models.Appointment).filter(models.Appointment.reader_id == user.id, models.Appointment.status.in_(['scheduled','in_progress'])).order_by(models.Appointment.start_time).all()
    return {
        "upcoming": [{"booking_uid": a.booking_uid, "client_id": a.client_id, "mode": a.mode, "start_time": a.start_time, "length_minutes": a.length_minutes, "status": a.status} for a in upcoming]
    }

@router.post("/book")
async def book(payload: dict, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    reader_id = int(payload.get('reader_id'))
    mode = payload.get('mode')
    length = int(payload.get('length_minutes'))
    start_time_str = payload.get('start_time')
    if mode not in {'chat','voice','video'}:
        raise HTTPException(400, 'Invalid mode')
    if length not in ALLOWED_LENGTHS:
        raise HTTPException(400, 'Invalid length')
    try:
        start_time = datetime.fromisoformat(start_time_str)
    except Exception:
        raise HTTPException(400, 'Invalid start_time')
    end_time = start_time + timedelta(minutes=length)

    client = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    reader = db.query(models.User).filter(models.User.id == reader_id).one_or_none()
    if not reader or reader.role != 'reader':
        raise HTTPException(404, 'Reader not found')
    rp = db.query(models.ReaderProfile).filter(models.ReaderProfile.user_id == reader_id).one_or_none()
    if not rp:
        raise HTTPException(400, 'Reader profile missing')

    # Ensure availability: check availability_blocks has a covering block and no overlapping appointments
    block = db.query(models.AvailabilityBlock).filter(models.AvailabilityBlock.reader_id == reader_id, models.AvailabilityBlock.start_time <= start_time, models.AvailabilityBlock.end_time >= end_time).one_or_none()
    if not block:
        raise HTTPException(409, 'Requested time not available')
    overlapping = db.query(models.Appointment).filter(models.Appointment.reader_id == reader_id, models.Appointment.status.in_(['scheduled','in_progress']), models.Appointment.start_time < end_time, models.Appointment.end_time > start_time).count()
    if overlapping:
        raise HTTPException(409, 'Time already booked')

    price_cents = compute_price_cents(rp, mode, length)

    # Debit client wallet now; reader is credited upon completion to allow refunds
    from ..services.wallet import debit
    debit(db, client.id, price_cents, ref_type='appointment', ref_id='pending')

    appt = models.Appointment(
        booking_uid=secrets.token_urlsafe(12),
        reader_id=reader_id,
        client_id=client.id,
        length_minutes=length,
        mode=mode,
        price_cents=price_cents,
        start_time=start_time,
        end_time=end_time,
        status='scheduled'
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return {"booking_uid": appt.booking_uid, "start_time": appt.start_time, "end_time": appt.end_time, "price_cents": price_cents}

@router.post("/{booking_uid}/cancel")
async def cancel(booking_uid: str, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    appt = db.query(models.Appointment).filter(models.Appointment.booking_uid == booking_uid).one_or_none()
    if not appt:
        raise HTTPException(404, 'Not found')
    if appt.client_id != user.id and user.role != 'admin' and user.id != appt.reader_id:
        raise HTTPException(403, 'Not permitted')
    if appt.status not in {'scheduled'}:
        raise HTTPException(400, 'Cannot cancel now')
    now = datetime.utcnow()
    delta = appt.start_time - now
    # refund policy
    if delta.total_seconds() >= 24*3600:
        refund_pct = 100
    elif delta.total_seconds() >= 3600:
        refund_pct = 50
    else:
        refund_pct = 0
    refund = appt.price_cents * refund_pct // 100
    if refund > 0:
        from ..services.wallet import credit
        credit(db, appt.client_id, refund, ref_type='refund', ref_id=appt.booking_uid)
    appt.status = 'canceled'
    db.add(appt)
    db.commit()
    return {"ok": True, "refund_cents": refund}

@router.post("/{booking_uid}/start")
async def start(booking_uid: str, token=Depends(get_current_user_token), db: Session = Depends(get_db)):
    # Either party can start at or after start_time
    user = db.query(models.User).filter(models.User.clerk_user_id == token.get('sub')).one()
    appt = db.query(models.Appointment).filter(models.Appointment.booking_uid == booking_uid).one_or_none()
    if not appt:
        raise HTTPException(404, 'Not found')
    if user.id not in {appt.client_id, appt.reader_id}:
        raise HTTPException(403, 'Not permitted')
    now = datetime.utcnow()
    if now < appt.start_time - timedelta(minutes=5):
        raise HTTPException(400, 'Too early to start')
    if appt.status not in {'scheduled','in_progress'}:
        raise HTTPException(400, 'Invalid state')
    # Create or reuse session
    sess = db.query(models.Session).filter(models.Session.appointment_id == appt.id).one_or_none()
    import secrets as _secrets
    if not sess:
        sess = models.Session(
            session_uid=_secrets.token_urlsafe(12),
            reader_id=appt.reader_id,
            client_id=appt.client_id,
            mode=appt.mode,
            status='active',
            started_at=now,
            per_minute=False,
            appointment_id=appt.id,
        )
        db.add(sess)
        appt.status = 'in_progress'
        db.add(appt)
        db.commit()
        db.refresh(sess)
    return {"session_uid": sess.session_uid}