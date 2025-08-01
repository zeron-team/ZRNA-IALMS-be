# backend/app/repositories/reporting_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models

def get_dashboard_stats(db: Session):
    """Calcula estadísticas generales de la plataforma."""
    total_users = db.query(db_models.User).count()
    total_courses = db.query(db_models.Course).count()
    # CORRECCIÓN: Usa el nombre de la CLASE, no el de la tabla
    total_enrollments = db.query(db_models.CourseEnrollment).count()
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
    }

def get_courses_with_enrollments(db: Session):
    """
    Obtiene todos los cursos con la lista de estudiantes inscritos en cada uno.
    """
    # CORRECCIÓN: Usa la relación real 'enrollments', no la propiedad 'enrolled_students'
    return db.query(db_models.Course).options(
        joinedload(db_models.Course.enrollments).joinedload(db_models.CourseEnrollment.user).joinedload(db_models.User.profile)
    ).all()