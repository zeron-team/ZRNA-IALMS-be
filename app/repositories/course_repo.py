# backend/app/repositories/course_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models
from app.models import course as course_schemas

def get_all_courses(db: Session):
    return db.query(db_models.Course).options(
        joinedload(db_models.Course.category) # <-- Carga la categoría
    ).all()

def get_course_by_id(db: Session, course_id: int):
    """Obtiene un curso por ID, incluyendo su categoría."""
    return db.query(db_models.Course).filter(
        db_models.Course.id == course_id
    ).options(
        joinedload(db_models.Course.category)
    ).first()

def create_course(db: Session, course: course_schemas.CourseCreate, instructor_id: int):
    """Crea un nuevo curso en la base de datos."""
    db_course = db_models.Course(
        title=course.title,
        description=course.description,
        instructor_id=instructor_id,
        category_id = course.category_id,
        level = course.level
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def add_modules_to_course(db: Session, course_id: int, modules: list):
    """Añade una lista de módulos a un curso existente."""
    for module_data in modules:
        db_module = db_models.Module(
            course_id=course_id,
            title=module_data['title'],
            description=module_data['description'],
            order_index=module_data['order_index']
        )
        db.add(db_module)
    db.commit()

def get_courses_by_instructor_id(db: Session, instructor_id: int):
    return db.query(db_models.Course).filter(
        db_models.Course.instructor_id == instructor_id
    ).options(
        joinedload(db_models.Course.category) # <-- Carga la categoría
    ).all()

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