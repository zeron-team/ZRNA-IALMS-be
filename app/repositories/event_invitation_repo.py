from sqlalchemy.orm import Session
from app import db_models

def create_event_invitation(db: Session, event_id: int, user_id: int, status: str = "pending"):
    db_invitation = db_models.EventInvitation(event_id=event_id, user_id=user_id, status=status)
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    return db_invitation

def get_event_invitation(db: Session, invitation_id: int):
    return db.query(db_models.EventInvitation).filter(db_models.EventInvitation.id == invitation_id).first()

def update_event_invitation_status(db: Session, invitation_id: int, status: str):
    db_invitation = db.query(db_models.EventInvitation).filter(db_models.EventInvitation.id == invitation_id).first()
    if db_invitation:
        db_invitation.status = status
        db.commit()
        db.refresh(db_invitation)
        return db_invitation
    return None

def get_pending_invitations_for_user(db: Session, user_id: int):
    return db.query(db_models.EventInvitation).filter(
        db_models.EventInvitation.user_id == user_id,
        db_models.EventInvitation.status == 'pending'
    ).all()