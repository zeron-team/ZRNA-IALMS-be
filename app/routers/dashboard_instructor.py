# backend/app/routers/dashboard_instructor.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.security import instructor_required
from app.models.user import User as UserSchema
from app.repositories import reporting_repo

router = APIRouter(
    prefix="/dashboard/instructor",
    tags=["Dashboard Instructor"],
    dependencies=[Depends(instructor_required)]
)

@router.get("/")
def get_instructor_dashboard_data(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    """Recopila todos los datos para el dashboard del instructor."""
    return {
        "room_summary": reporting_repo.get_rooms_summary_by_instructor(db, instructor_id=current_user.id),
        "student_progress": reporting_repo.get_student_progress_for_instructor_courses(db, instructor_id=current_user.id),
        "personal_progress": reporting_repo.get_enrolled_courses_with_progress(db, user_id=current_user.id)
    }

@router.get("/student-progress")
def get_student_progress_summary(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    """Obtiene un resumen del progreso de todos los estudiantes."""
    return reporting_repo.get_all_student_progress_summary(db, instructor_id=current_user.id)

@router.get("/student-progress-detailed")
def get_detailed_student_progress_endpoint(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    """Obtiene el reporte detallado del progreso de los alumnos."""
    return reporting_repo.get_detailed_student_progress(db, instructor_id=current_user.id)