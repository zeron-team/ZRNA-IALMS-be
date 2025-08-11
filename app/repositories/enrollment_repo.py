# backend/app/repositories/enrollment_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models

def create_enrollment(db: Session, user_id: int, course_id: int):
    """Crea una nueva inscripción si no existe."""
    existing_enrollment = db.query(db_models.CourseEnrollment).filter_by(
        user_id=user_id, course_id=course_id
    ).first()

    if not existing_enrollment:
        enrollment = db_models.CourseEnrollment(user_id=user_id, course_id=course_id)
        db.add(enrollment)
        db.commit()


def get_enrolled_courses(db: Session, user_id: int):
    """Obtiene los cursos en los que un usuario está inscrito."""
    user = db.query(db_models.User).options(
        joinedload(db_models.User.enrollments).joinedload(db_models.CourseEnrollment.course)
    ).filter(db_models.User.id == user_id).first()
    return [enrollment.course for enrollment in user.enrollments] if user else []

def is_enrolled(db: Session, user_id: int, course_id: int) -> bool:
    """Verifica si una inscripción específica existe."""
    return db.query(db_models.CourseEnrollment).filter_by(
        user_id=user_id, course_id=course_id
    ).first() is not None