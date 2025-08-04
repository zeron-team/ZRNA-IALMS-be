#backend/app/routers/admin.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.security import admin_required
from app.repositories import reporting_repo
from app.models.admin import DashboardStats, CourseEnrollmentStats

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(admin_required)]
)


@router.get("/dashboard-stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    """Obtiene estadísticas para el dashboard principal."""
    return reporting_repo.get_dashboard_stats(db)


@router.get("/enrollments", response_model=List[CourseEnrollmentStats])
def get_detailed_enrollments(db: Session = Depends(get_db)):
    """
    Obtiene los cursos y la CANTIDAD de estudiantes inscritos en cada uno.
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