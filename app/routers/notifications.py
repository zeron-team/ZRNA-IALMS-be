# backend/app/routers/notifications.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.security import get_current_active_user
from app.models.user import User as UserSchema
from app.models.notification import Notification as NotificationSchema
from app.repositories import notification_repo

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

@router.get("/", response_model=List[NotificationSchema])
def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene todas las notificaciones para el usuario actual."""
    return notification_repo.get_notifications_for_user(db, user_id=current_user.id)

@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Marca una notificación como leída."""
    success = notification_repo.mark_as_read(db, notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notificación no encontrada.")
    return None