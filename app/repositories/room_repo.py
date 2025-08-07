# backend/app/repositories/room_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models
import secrets

def create_room(db: Session, name: str, description: str, instructor_id: int):
    join_code = secrets.token_hex(4).upper() # Genera un código de 8 caracteres
    db_room = db_models.Room(
        name=name,
        description=description,
        instructor_id=instructor_id,
        join_code=join_code
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_rooms_by_instructor_id(db: Session, instructor_id: int):
    """Obtiene todas las salas creadas por un instructor."""
    return db.query(db_models.Room).filter(db_models.Room.instructor_id == instructor_id).all()

def get_room_by_id(db: Session, room_id: int):
    """Obtiene una sala por su ID."""
    return db.query(db_models.Room).filter(db_models.Room.id == room_id).first()

def get_room_by_id_with_details(db: Session, room_id: int):
    """
    Obtiene una sala por su ID, cargando explícitamente sus cursos y miembros.
    """
    return db.query(db_models.Room).options(
        joinedload(db_models.Room.courses),
        joinedload(db_models.Room.members).joinedload(db_models.User.profile)
    ).filter(db_models.Room.id == room_id).first()


def get_rooms_for_member(db: Session, user_id: int):
    """Obtiene las salas a las que un usuario pertenece como miembro."""
    return db.query(db_models.Room).join(
        db_models.RoomMember, db_models.Room.id == db_models.RoomMember.room_id
    ).filter(db_models.RoomMember.user_id == user_id).all()

def add_course_to_room(db: Session, room_id: int, course_id: int, instructor_id: int):
    """Añade un curso a una sala, verificando que el instructor sea el dueño."""
    db_room = db.query(db_models.Room).filter(
        db_models.Room.id == room_id,
        db_models.Room.instructor_id == instructor_id
    ).first()

    if not db_room:
        return None

    existing_link = db.query(db_models.RoomCourse).filter_by(room_id=room_id, course_id=course_id).first()
    if not existing_link:
        db_room_course = db_models.RoomCourse(room_id=room_id, course_id=course_id)
        db.add(db_room_course)
        db.commit()

    # Devuelve siempre el objeto de la sala para que la respuesta sea válida
    db.refresh(db_room)
    return db_room

def add_member_to_room(db: Session, room_id: int, user_id: int, instructor_id: int):
    """Añade un miembro a una sala, verificando que el instructor sea el dueño."""
    db_room = db.query(db_models.Room).filter(
        db_models.Room.id == room_id,
        db_models.Room.instructor_id == instructor_id
    ).first()

    if not db_room:
        return None

    # Evita añadir miembros duplicados
    existing_member = db.query(db_models.RoomMember).filter_by(room_id=room_id, user_id=user_id).first()
    if existing_member:
        return db_room

    db_room_member = db_models.RoomMember(room_id=room_id, user_id=user_id)
    db.add(db_room_member)
    db.commit()
    return db_room