# backend/app/repositories/enrollment_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models

def create_enrollment(db: Session, user_id: int, course_id: int):
    user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    course = db.query(db_models.Course).filter(db_models.Course.id == course_id).first()
    if user and course and course not in user.enrolled_courses:
        # La forma correcta de crear la asociación a través del modelo intermedio
        enrollment = db_models.CourseEnrollment(user_id=user_id, course_id=course_id)
        db.add(enrollment)
        db.commit()


def get_enrolled_courses(db: Session, user_id: int):
    """
    Obtiene el usuario y carga explícitamente sus inscripciones y los cursos asociados.
    """
    user = db.query(db_models.User).options(
        joinedload(db_models.User.enrollments).joinedload(db_models.CourseEnrollment.course)
    ).filter(db_models.User.id == user_id).first()

    return [enrollment.course for enrollment in user.enrollments] if user else []

def is_enrolled(db: Session, user_id: int, course_id: int) -> bool:
    enrollment = db.query(db_models.CourseEnrollment).filter_by(
        user_id=user_id, course_id=course_id
    ).first()
    return enrollment is not None