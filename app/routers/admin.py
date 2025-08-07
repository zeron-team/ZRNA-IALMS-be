#backend/app/routers/admin.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.security import instructor_required  # Se usa la dependencia que incluye a ambos roles
from app.repositories import reporting_repo
from app.models.admin import DashboardStats, CourseEnrollmentStats

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(instructor_required)]  # Se aplica a todas las rutas de este archivo
)


@router.get("/dashboard-stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    """Obtiene estadísticas generales para el dashboard."""
    return reporting_repo.get_dashboard_stats(db)


@router.get("/enrollments", response_model=List[CourseEnrollmentStats])
def get_detailed_enrollments(db: Session = Depends(get_db)):
    """
    Obtiene los cursos y la cantidad de estudiantes inscritos en cada uno.
    """
    courses = reporting_repo.get_courses_with_enrollments(db)

    stats = []
    for course in courses:
        stats.append(
            CourseEnrollmentStats(
                id=course.id,
                title=course.title,
                enrollment_count=len(course.enrollments)
            )
        )
    return stats

@router.get("/rooms-summary")
def get_all_rooms_summary_endpoint(db: Session = Depends(get_db)):
    """Obtiene un resumen de todas las salas de la plataforma."""
    return reporting_repo.get_all_rooms_summary(db)