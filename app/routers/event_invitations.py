from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.repositories import event_invitation_repo, scheduled_event_repo
from app.security import get_current_active_user
from app.models.user import User as UserSchema
from app.models.scheduled_event import EventInvitation, EventInvitationCreate
from app.repositories import notification_repo

router = APIRouter(prefix="/event-invitations", tags=["Event Invitations"])

@router.get("/pending", response_model=List[EventInvitation])
def get_pending_invitations(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    return event_invitation_repo.get_pending_invitations_for_user(db, user_id=current_user.id)

@router.post("/{invitation_id}/accept", response_model=EventInvitation)
def accept_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    db_invitation = event_invitation_repo.get_event_invitation(db, invitation_id)
    if not db_invitation or db_invitation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Invitación no encontrada o no tienes permiso.")

    if db_invitation.status != 'pending':
        raise HTTPException(status_code=400, detail="La invitación ya ha sido respondida.")

    updated_invitation = event_invitation_repo.update_event_invitation_status(db, invitation_id, 'accepted')
    if not updated_invitation:
        raise HTTPException(status_code=500, detail="No se pudo aceptar la invitación.")

    # Notify the event creator
    event = scheduled_event_repo.get_scheduled_event_by_id(db, event_id=updated_invitation.event_id)
    if event:
        message = f"{current_user.username} ha aceptado tu invitación al evento '{event.title}'."
        notification_repo.create_notification(db, user_id=event.creator_id, message=message, link_url=f"/calendar?event_id={event.id}")

    return updated_invitation

@router.post("/{invitation_id}/reject", response_model=EventInvitation)
def reject_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    db_invitation = event_invitation_repo.get_event_invitation(db, invitation_id)
    if not db_invitation or db_invitation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Invitación no encontrada o no tienes permiso.")

    if db_invitation.status != 'pending':
        raise HTTPException(status_code=400, detail="La invitación ya ha sido respondida.")

    updated_invitation = event_invitation_repo.update_event_invitation_status(db, invitation_id, 'rejected')
    if not updated_invitation:
        raise HTTPException(status_code=500, detail="No se pudo rechazar la invitación.")

    # Notify the event creator
    event = scheduled_event_repo.get_scheduled_event_by_id(db, event_id=updated_invitation.event_id)
    if event:
        message = f"{current_user.username} ha rechazado tu invitación al evento '{event.title}'."
        notification_repo.create_notification(db, user_id=event.creator_id, message=message, link_url=f"/calendar?event_id={event.id}")

    return updated_invitation