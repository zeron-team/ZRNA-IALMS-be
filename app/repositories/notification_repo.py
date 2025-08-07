# backend/app/repositories/notification_repo.py

from sqlalchemy.orm import Session
from app import db_models

def create_notification(db: Session, user_id: int, message: str, link_url: str):
    db_notification = db_models.Notification(
        user_id=user_id,
        message=message,
        link_url=link_url
    )
    db.add(db_notification)
    db.commit()

def get_notifications_for_user(db: Session, user_id: int):
    """Obtiene las notificaciones de un usuario, las más recientes primero."""
    return db.query(db_models.Notification).filter(
        db_models.Notification.user_id == user_id
    ).order_by(db_models.Notification.created_at.desc()).all()


def mark_as_read(db: Session, notification_id: int, user_id: int) -> bool:
    """Marca una notificación como leída, verificando que pertenezca al usuario."""
    notification = db.query(db_models.Notification).filter(
        db_models.Notification.id == notification_id,
        db_models.Notification.user_id == user_id
    ).first()

    if notification:
        notification.is_read = True
        db.commit()
        return True
    return False