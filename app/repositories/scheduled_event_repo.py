from sqlalchemy.orm import Session, joinedload
from app import db_models
from datetime import datetime
from app.db_models import EventInvitation

def create_scheduled_event(db: Session, room_id: int, creator_id: int, title: str, start_time: datetime, end_time: datetime, event_type: str):
    db_event = db_models.ScheduledEvent(room_id=room_id, creator_id=creator_id, title=title, start_time=start_time, end_time=end_time, event_type=event_type)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_scheduled_event_by_id(db: Session, event_id: int):
    return db.query(db_models.ScheduledEvent).options(joinedload(db_models.ScheduledEvent.invitations).joinedload(db_models.EventInvitation.user)).filter(db_models.ScheduledEvent.id == event_id).first()

def delete_scheduled_event(db: Session, event_id: int):
    db_event = db.query(db_models.ScheduledEvent).filter(db_models.ScheduledEvent.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
        return True
    return False

def update_scheduled_event(db: Session, event_id: int, event_data: dict):
    db_event = db.query(db_models.ScheduledEvent).filter(db_models.ScheduledEvent.id == event_id).first()
    if db_event:
        for key, value in event_data.items():
            if key != "invited_user_ids": # Handle invited_user_ids separately
                setattr(db_event, key, value)

        # Handle invited_user_ids: add new invitations, remove old ones
        current_invited_ids = {inv.user_id for inv in db_event.invitations}
        new_invited_ids = set(event_data.get("invited_user_ids", []))

        # Add new invitations
        for user_id in new_invited_ids - current_invited_ids:
            db_invitation = db_models.EventInvitation(event_id=event_id, user_id=user_id, status="pending")
            db.add(db_invitation)

        # Remove old invitations
        for user_id in current_invited_ids - new_invited_ids:
            db.query(db_models.EventInvitation).filter(
                db_models.EventInvitation.event_id == event_id,
                db_models.EventInvitation.user_id == user_id
            ).delete()

        db.commit()
        db.refresh(db_event)
        return db_event
    return None

def get_scheduled_events_for_user(db: Session, user_id: int):
    # Events created by the user
    created_events = db.query(db_models.ScheduledEvent).options(joinedload(db_models.ScheduledEvent.invitations).joinedload(db_models.EventInvitation.user)).filter(db_models.ScheduledEvent.creator_id == user_id).all()

    # Events where the user is invited (pending or accepted)
    invited_events_with_status = db.query(
        db_models.ScheduledEvent,
        db_models.EventInvitation.status
    ).options(joinedload(db_models.ScheduledEvent.invitations).joinedload(db_models.EventInvitation.user)).join(db_models.EventInvitation).filter(
        db_models.EventInvitation.user_id == user_id,
        db_models.EventInvitation.status.in_(['pending', 'accepted'])
    ).all()

    # Prepare invited events with their invitation status
    processed_invited_events = []
    for event, status in invited_events_with_status:
        event.invitation_status = status
        processed_invited_events.append(event)

    # Combine and return unique events
    all_events = {event.id: event for event in created_events + processed_invited_events}.values()
    return list(all_events)