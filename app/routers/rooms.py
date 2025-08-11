# backend/app/routers/rooms.py

from fastapi import APIRouter, Depends, HTTPException,  status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.dependencies import get_db
from app.repositories import room_repo
from app.security import instructor_required, get_current_active_user
from app.models.user import User as UserSchema
from app.models.room import Room, RoomCreate
from app import db_models
from app.repositories import notification_repo

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/", response_model=Room)
def create_new_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required) # Solo instructores pueden crear
):
    """
    Crea una nueva sala con límites para el plan gratuito.
    """
    room_count = room_repo.count_rooms_by_instructor(db, instructor_id=current_user.id)

    # --- LÓGICA DE LÍMITES AÑADIDA ---
    if room_count >= 1:
        raise HTTPException(status_code=403, detail="Has alcanzado el límite de 1 sala para el plan gratuito de instructor.")

    return room_repo.create_room(
        db, name=room.name, description=room.description, instructor_id=current_user.id
    )

@router.get("/", response_model=List[Room])
def get_my_rooms(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene las salas creadas por el instructor o a las que pertenece el estudiante."""
    if current_user.role.name in ['instructor', 'admin']:
        return room_repo.get_rooms_by_instructor_id(db, instructor_id=current_user.id)
    else: # Si es estudiante
        return room_repo.get_rooms_for_member(db, user_id=current_user.id)

@router.get("/{room_id}", response_model=Room)
def get_room_details(
        room_id: int,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene los detalles de una sala, validando los permisos."""
    db_room = room_repo.get_room_by_id_with_details(db, room_id=room_id)

    if not db_room:
        raise HTTPException(status_code=404, detail="Sala no encontrada")

    # --- LÓGICA DE PERMISOS ---
    is_instructor = db_room.instructor_id == current_user.id
    is_member = any(member.id == current_user.id for member in db_room.members)

    if not is_instructor and not is_member:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta sala.")

    return db_room

@router.post("/{room_id}/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_course_to_room_endpoint(
        room_id: int,
        course_id: int,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(instructor_required)
):
    """Asocia un curso existente a una sala."""
    success = room_repo.add_course_to_room(
        db, room_id=room_id, course_id=course_id, instructor_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Sala no encontrada o no tienes permiso.")

    return None  # No se devuelve contenido, solo el código 204

@router.post("/{room_id}/members/{user_id}", response_model=Room)
def add_member_to_room_endpoint(
    room_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    updated_room = room_repo.add_member_to_room(
        db, room_id=room_id, user_id=user_id, instructor_id=current_user.id
    )
    if not updated_room:
        raise HTTPException(status_code=404, detail="Sala no encontrada o no tienes permiso.")

    message = f"Has sido invitado a la sala: '{updated_room.name}'"
    link = f"/rooms/{room_id}"
    notification_repo.create_notification(db, user_id=user_id, message=message, link_url=link)

    return updated_room


@router.delete("/{room_id}/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_course_from_room_endpoint(
    room_id: int, course_id: int, db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    success = room_repo.remove_course_from_room(db, room_id, course_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Asociación no encontrada o no tienes permiso.")
    return

@router.delete("/{room_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member_from_room_endpoint(
    room_id: int, user_id: int, db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    success = room_repo.remove_member_from_room(db, room_id, user_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Miembro no encontrado o no tienes permiso.")
    return


@router.put("/{room_id}", response_model=Room)
def update_existing_room(
    room_id: int,
    room_update: RoomCreate, # Reutilizamos el schema de creación
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    """Actualiza una sala existente."""
    updated_room = room_repo.update_room(
        db,
        room_id=room_id,
        name=room_update.name,
        description=room_update.description,
        instructor_id=current_user.id
    )
    if not updated_room:
        raise HTTPException(status_code=404, detail="Sala no encontrada o no tienes permiso.")
    return updated_room