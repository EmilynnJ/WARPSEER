from sqlalchemy.orm import Session
from .. import models
from ..config import settings
import httpx
from typing import Optional, List
import json

def create_notification(db: Session, user_id: int, title: str, body: str, type: str):
    """Create an in-app notification"""
    notif = models.Notification(
        user_id=user_id,
        title=title,
        body=body,
        type=type
    )
    db.add(notif)
    db.flush()
    return notif

async def send_push_notification(user_id: int, title: str, body: str, data: Optional[dict] = None):
    """Send push notification via OneSignal"""
    if not settings.enable_push_notifications or not settings.onesignal_app_id:
        return
    
    db = Session()
    try:
        # Get user's push subscriptions
        subs = db.query(models.PushSubscription).filter(
            models.PushSubscription.user_id == user_id,
            models.PushSubscription.active == True
        ).all()
        
        if not subs:
            return
        
        player_ids = [s.player_id for s in subs]
        
        # Send via OneSignal API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://onesignal.com/api/v1/notifications',
                headers={
                    'Authorization': f'Basic {settings.onesignal_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'app_id': settings.onesignal_app_id,
                    'include_player_ids': player_ids,
                    'headings': {'en': title},
                    'contents': {'en': body},
                    'data': data or {},
                    'ios_badgeType': 'Increase',
                    'ios_badgeCount': 1
                }
            )
            return response.json()
    finally:
        db.close()

async def notify_session_request(db: Session, reader_id: int, session_uid: str):
    """Notify reader of new session request"""
    title = "New Reading Request"
    body = "You have a new reading request waiting"
    
    # In-app notification
    create_notification(db, reader_id, title, body, 'session_request')
    
    # Push notification
    await send_push_notification(
        reader_id, 
        title, 
        body,
        {'type': 'session_request', 'session_uid': session_uid}
    )

async def notify_appointment_reminder(db: Session, user_id: int, appointment: models.Appointment, minutes_before: int):
    """Send appointment reminder"""
    title = f"Appointment Reminder"
    body = f"Your reading starts in {minutes_before} minutes"
    
    create_notification(db, user_id, title, body, 'appointment_reminder')
    
    await send_push_notification(
        user_id,
        title,
        body,
        {'type': 'appointment_reminder', 'booking_uid': appointment.booking_uid}
    )