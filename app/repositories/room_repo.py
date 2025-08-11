# backend/app/repositories/room_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models
import secrets


def create_room(db: Session, name: str, description: str, instructor_id: int):
    """Crea una nueva sala en la base de datos."""
    join_code = secrets.token_hex(4).upper()
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
    """Obtiene una sala por su ID, cargando sus cursos y miembros."""
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

    existing_member = db.query(db_models.RoomMember).filter_by(room_id=room_id, user_id=user_id).first()
    if not existing_member:
        db_room_member = db_models.RoomMember(room_id=room_id, user_id=user_id)
        db.add(db_room_member)
        db.commit()

    # Devuelve siempre el objeto de la sala para que la respuesta sea válida
    db.refresh(db_room)
    return db_room


def remove_course_from_room(db: Session, room_id: int, course_id: int, instructor_id: int) -> bool:
    """Elimina la asociación de un curso de una sala, verificando al instructor."""
    db_room = db.query(db_models.Room).filter_by(id=room_id, instructor_id=instructor_id).first()
    if not db_room:
        return False

    link = db.query(db_models.RoomCourse).filter_by(room_id=room_id, course_id=course_id).first()
    if link:
        db.delete(link)
        db.commit()
        return True
    return False


def remove_member_from_room(db: Session, room_id: int, user_id: int, instructor_id: int) -> bool:
    """Elimina a un miembro de una sala, verificando al instructor."""
    db_room = db.query(db_models.Room).filter_by(id=room_id, instructor_id=instructor_id).first()
    if not db_room:
        return False

    member = db.query(db_models.RoomMember).filter_by(room_id=room_id, user_id=user_id).first()
    if member:
        db.delete(member)
        db.commit()
        return True
    return False


def update_room(db: Session, room_id: int, name: str, description: str, instructor_id: int):
    """Actualiza el nombre y la descripción de una sala, verificando al instructor."""
    db_room = db.query(db_models.Room).filter(
        db_models.Room.id == room_id,
        db_models.Room.instructor_id == instructor_id
    ).first()

    if db_room:
        db_room.name = name
        db_room.description = description
        db.commit()
        db.refresh(db_room)

    return db_room

# --- FUNCIÓN AÑADIDA ---
def count_rooms_by_instructor(db: Session, instructor_id: int) -> int:
    """Cuenta la cantidad de salas creadas por un instructor."""
    return db.query(db_models.Room).filter(db_models.Room.instructor_id == instructor_id).count()