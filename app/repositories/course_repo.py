# backend/app/repositories/course_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models
from app.models import course as course_schemas

def get_all_courses(db: Session):
    """Obtiene todos los cursos, cargando su categoría."""
    return db.query(db_models.Course).options(
        joinedload(db_models.Course.category)
    ).all()

def get_published_courses(db: Session):
    """
    Obtiene todos los cursos publicados, cargando su categoría de forma segura.
    """

    # --- CONSULTA CORREGIDA ---
    # Usamos outerjoin para asegurarnos de que la consulta no falle
    # si un curso no tiene una categoría (category_id es NULL).
    return db.query(db_models.Course).outerjoin(
        db_models.Category
    ).filter(
        db_models.Course.status == 'published'
    ).options(
        joinedload(db_models.Course.category)
    ).all()

def get_course_by_id(db: Session, course_id: int):
    """Obtiene un curso por ID, cargando su categoría."""
    return db.query(db_models.Course).filter(
        db_models.Course.id == course_id
    ).options(
        joinedload(db_models.Course.category)
    ).first()

def get_courses_by_instructor_id(db: Session, instructor_id: int):
    """Obtiene los cursos de un instructor específico."""
    return db.query(db_models.Course).filter(
        db_models.Course.instructor_id == instructor_id
    ).options(
        joinedload(db_models.Course.category)
    ).all()

# --- FUNCIÓN NUEVA Y CLAVE ---
def get_courses_created_by_user(db: Session, user_id: int):
    """Obtiene los cursos creados por un usuario (estudiante)."""
    return db.query(db_models.Course).filter(
        db_models.Course.creator_id == user_id
    ).options(
        joinedload(db_models.Course.category)
    ).all()

def count_courses_created_by_user(db: Session, user_id: int) -> int:
    """Cuenta los cursos creados por un estudiante."""
    return db.query(db_models.Course).filter(db_models.Course.creator_id == user_id).count()


def create_instructor_course(db: Session, course: course_schemas.CourseCreate, instructor_id: int):
    # Lógica para manejar el precio
    price = course.price if not course.is_free else 0.0

    db_course = db_models.Course(
        title=course.title,
        description=course.description,
        instructor_id=instructor_id,
        category_id=course.category_id,
        level=course.level,
        is_free=course.is_free,  # <-- Nuevo campo
        price=price,  # <-- Precio ajustado
        status='published'
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def create_student_course(db: Session, course: course_schemas.CourseCreate, creator_id: int):
    """Crea un curso asignado a un estudiante como creador."""
    db_course = db_models.Course(
        title=course.title,
        description=course.description,
        creator_id=creator_id,
        category_id=course.category_id,
        level=course.level,
        status='draft',
        visibility='private',
        is_free=True, # Por defecto, los cursos de estudiantes son gratis
        price=0.0
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def add_modules_to_course(db: Session, course_id: int, modules: list):
    """Añade una lista de módulos a un curso."""
    for module_data in modules:
        db_module = db_models.Module(
            course_id=course_id,
            title=module_data.get('title'),
            description=module_data.get('description'),
            order_index=module_data.get('order_index'),
            has_example=module_data.get('has_example', False),
            context=module_data.get('context'),
            skill_type=module_data.get('skill_type'),
            diagram_mermaid_syntax=module_data.get('diagram_mermaid_syntax')
        )
        db.add(db_module)
    db.commit()

def update_course(db: Session, course_id: int, course_update: course_schemas.CourseCreate, user_id: int):
    """Actualiza un curso, verificando que el usuario sea el propietario."""
    db_course = db.query(db_models.Course).filter(
        db_models.Course.id == course_id,
        db_models.Course.instructor_id == user_id
    ).first()

    if db_course:
        db_course.title = course_update.title
        db_course.description = course_update.description
        db_course.category_id = course_update.category_id
        db_course.level = course_update.level
        db.commit()
        db.refresh(db_course)
    return db_course

def delete_course(db: Session, course_id: int, user_id: int) -> bool:
    """Elimina un curso, verificando que el usuario sea el propietario."""
    db_course = db.query(db_models.Course).filter(
        db_models.Course.id == course_id,
        db_models.Course.instructor_id == user_id
    ).first()

    if db_course:
        db.delete(db_course)
        db.commit()
        return True
    return False

def get_published_courses(db: Session):
    """Obtiene todos los cursos con estado 'published'."""
    return db.query(db_models.Course).filter(
        db_models.Course.status == 'published'
    ).options(
        joinedload(db_models.Course.category)
    ).all()

def count_courses_by_instructor(db: Session, instructor_id: int) -> int:
    """Cuenta la cantidad de cursos creados por un instructor."""
    return db.query(db_models.Course).filter(db_models.Course.instructor_id == instructor_id).count()