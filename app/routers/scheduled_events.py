from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.repositories import scheduled_event_repo, room_repo, event_invitation_repo, notification_repo
from app.security import instructor_required, get_current_active_user
from app.models.user import User as UserSchema
from app.models.scheduled_event import ScheduledEvent, ScheduledEventCreate

router = APIRouter(prefix="/scheduled-events", tags=["Scheduled Events"])

@router.post("/", response_model=ScheduledEvent, status_code=status.HTTP_201_CREATED)
def create_scheduled_event(
    event: ScheduledEventCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    # Verify that the room exists and the current user is the instructor of that room
    room = room_repo.get_room_by_id(db, room_id=event.room_id)
    if not room or room.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para programar eventos en esta sala.")

    db_event = scheduled_event_repo.create_scheduled_event(
        db, room_id=event.room_id, creator_id=current_user.id, title=event.title, start_time=event.start_time, end_time=event.end_time, event_type=event.event_type
    )

    # Create invitations for invited users
    for user_id in event.invited_user_ids:
        event_invitation_repo.create_event_invitation(db, event_id=db_event.id, user_id=user_id)
        # Create a notification for the invited user
        notification_repo.create_notification(
            db,
            user_id=user_id,
            message=f"Has sido invitado al evento '{event.title}' en la sala '{room.name}'.",
            link_url=f"/calendar?event_id={db_event.id}" # Assuming a link to the event in the calendar
        )

    return db_event

@router.get("/user-events", response_model=List[ScheduledEvent])
def get_scheduled_events_for_user(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    return scheduled_event_repo.get_scheduled_events_for_user(db, user_id=current_user.id)

@router.put("/{event_id}", response_model=ScheduledEvent)
def update_scheduled_event(
    event_id: int,
    event: ScheduledEventCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    # Verify that the event exists and the current user is the creator of the event
    db_event = scheduled_event_repo.get_scheduled_event_by_id(db, event_id=event_id)
    if not db_event or db_event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar este evento.")

    updated_event = scheduled_event_repo.update_scheduled_event(db, event_id, event.model_dump())
    if not updated_event:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el evento programado.")
    return updated_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheduled_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    # Verify that the event exists and the current user is the creator of the event
    event = scheduled_event_repo.get_scheduled_event_by_id(db, event_id=event_id)
    if not event or event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este evento.")

    if not scheduled_event_repo.delete_scheduled_event(db, event_id=event_id):
        raise HTTPException(status_code=500, detail="No se pudo eliminar el evento programado.")
    return