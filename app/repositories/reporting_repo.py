# backend/app/repositories/reporting_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models

def get_dashboard_stats(db: Session):
    """Calcula estadísticas generales de la plataforma."""
    total_users = db.query(db_models.User).count()
    total_courses = db.query(db_models.Course).count()
    total_enrollments = db.query(db_models.CourseEnrollment).count()
    total_categories = db.query(db_models.Category).count()
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "total_categories": total_categories,
    }

def get_courses_with_enrollments(db: Session):
    """
    Obtiene todos los cursos, cargando explícitamente la relación de inscripciones.
    """
    return db.query(db_models.Course).options(
        joinedload(db_models.Course.enrollments)
    ).all()