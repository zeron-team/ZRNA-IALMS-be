#backend/app/routers/admin.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.security import admin_required
from app.repositories import reporting_repo
from app.models.admin import DashboardStats, CourseWithEnrollments

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(admin_required)] # Protege todas las rutas de este router
)

@router.get("/dashboard-stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    """Obtiene estadísticas para el dashboard principal."""
    return reporting_repo.get_dashboard_stats(db)

@router.get("/enrollments", response_model=List[CourseWithEnrollments])
def get_detailed_enrollments(db: Session = Depends(get_db)):
    """Obtiene una lista de todos los cursos y los alumnos inscritos en cada uno."""
    return reporting_repo.get_courses_with_enrollments(db)