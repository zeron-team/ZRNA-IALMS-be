# backend/app/routers/enrollments.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.security import get_current_active_user
from app.models.user import User as UserSchema
from app.models.course import Course as CourseSchema
from app.repositories import enrollment_repo, progress_repo
from app.models.course import CourseWithProgress
from app.logic import course_logic

router = APIRouter(
    tags=["Enrollments"]
)


@router.post("/courses/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
def enroll_in_course(
        course_id: int,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_active_user)
):
    """Inscribe al usuario actual en un curso."""
    if enrollment_repo.is_enrolled(db, user_id=current_user.id, course_id=course_id):
        raise HTTPException(status_code=400, detail="Ya estás inscrito en este curso.")

    enrollment_repo.create_enrollment(db, user_id=current_user.id, course_id=course_id)
    return {"message": "Inscripción exitosa."}


@router.get("/my-courses", response_model=List[CourseWithProgress])
def get_my_enrolled_courses(
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_active_user)
):
    enrolled_courses = enrollment_repo.get_enrolled_courses(db, user_id=current_user.id)

    courses_with_data = []
    for course in enrolled_courses:
        total_modules = len(course.modules)
        completed_modules = progress_repo.get_completed_modules_count(db, current_user.id, course.id)
        percentage = round((completed_modules / total_modules) * 100) if total_modules > 0 else 0

        # --- LÓGICA DE ESTRELLAS AÑADIDA AQUÍ ---
        total, earned = course_logic.calculate_star_rating(db, course, current_user.id)

        course_data = CourseWithProgress(
            **course.__dict__,
            category=course.category,
            completion_percentage=percentage,
            total_stars=total,
            earned_stars=earned
        )
        courses_with_data.append(course_data)

    return courses_with_data