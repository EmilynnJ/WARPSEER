from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, DateTime, Boolean, Numeric, Text, UniqueConstraint
from .db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clerk_user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(16), default="client")  # client|reader|admin
    display_name: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReaderProfile(Base):
    __tablename__ = "reader_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    bio: Mapped[str] = mapped_column(Text, default="")
    avatar_url: Mapped[str] = mapped_column(String(512), default="")
    status: Mapped[str] = mapped_column(String(16), default="offline")  # offline|online|busy
    rate_chat_ppm: Mapped[int] = mapped_column(Integer, default=199)  # cents per minute
    rate_voice_ppm: Mapped[int] = mapped_column(Integer, default=299)
    rate_video_ppm: Mapped[int] = mapped_column(Integer, default=399)
    rate_scheduled_15: Mapped[int] = mapped_column(Integer, default=3000)
    rate_scheduled_30: Mapped[int] = mapped_column(Integer, default=6000)
    rate_scheduled_45: Mapped[int] = mapped_column(Integer, default=9000)
    rate_scheduled_60: Mapped[int] = mapped_column(Integer, default=12000)

class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    balance_cents: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(24))  # credit|debit|refund|adjustment
    amount_cents: Mapped[int] = mapped_column(Integer)
    ref_type: Mapped[str] = mapped_column(String(32))  # payment_intent|session|gift|order
    ref_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    mode: Mapped[str] = mapped_column(String(16))  # chat|voice|video|stream
    status: Mapped[str] = mapped_column(String(16), default="requested")  # requested|active|ended|canceled
    started_at: Mapped[datetime | None]
    ended_at: Mapped[datetime | None]
    total_seconds: Mapped[int] = mapped_column(Integer, default=0)
    amount_charged_cents: Mapped[int] = mapped_column(Integer, default=0)
    per_minute: Mapped[bool] = mapped_column(Boolean, default=True)
    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"), nullable=True)

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    length_minutes: Mapped[int] = mapped_column(Integer)  # 15/30/45/60
    mode: Mapped[str] = mapped_column(String(16))
    price_cents: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    status: Mapped[str] = mapped_column(String(16), default="scheduled")  # scheduled|canceled|completed|in_progress

class StripeAccount(Base):
    __tablename__ = "stripe_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    account_id: Mapped[str] = mapped_column(String(64), unique=True)
    details_submitted: Mapped[bool] = mapped_column(Boolean, default=False)

class CmsPage(Base):
    __tablename__ = "cms_pages"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    html_content: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AvailabilityBlock(Base):
    __tablename__ = "availability_blocks"
    id: Mapped[int] = mapped_column(primary_key=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    stripe_product_id: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(16))  # digital|physical|service
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Gift(Base):
    __tablename__ = "gifts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    price_cents: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String(512), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class ReaderBalance(Base):
    __tablename__ = "reader_balances"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    balance_cents: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReaderLedgerEntry(Base):
    __tablename__ = "reader_ledger_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    reader_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(24))  # credit|debit|payout
    amount_cents: Mapped[int] = mapped_column(Integer)
    ref_type: Mapped[str] = mapped_column(String(32))  # session|gift|order|transfer
    ref_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_uid: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_cents: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="created")  # created|paid|fulfilled|canceled

__all__ = [
    "User",
    "ReaderProfile",
    "Wallet",
    "LedgerEntry",
    "Session",
    "Message",
    "Appointment",
    "StripeAccount",
    "Product",
    "Order",
    "ReaderBalance",
    "ReaderLedgerEntry",
    "Gift",
]