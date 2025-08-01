# backend/app/routers/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.security import get_current_active_user
from app.models.user import User as UserSchema
from app.models.dashboard import StudentDashboardData, EnrolledCourseData
from app.repositories import progress_repo
from app.services import ai_service
from app.logic import course_logic

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/student", response_model=StudentDashboardData)
def get_student_dashboard(
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_active_user)
):
    enrolled_courses_from_db = current_user.enrolled_courses

    courses_with_progress = []
    enrolled_titles = []
    for course in enrolled_courses_from_db:
        total_modules = len(course.modules)
        completed_modules = progress_repo.get_completed_modules_count(db, current_user.id, course.id)
        completion_percentage = round((completed_modules / total_modules) * 100) if total_modules > 0 else 0

        # --- LÓGICA DE ESTRELLAS AÑADIDA AQUÍ ---
        total_stars, earned_stars = course_logic.calculate_star_rating(db, course, current_user.id)

        course_data_dict = {
            "id": course.id, "title": course.title, "description": course.description,
            "instructor_id": course.instructor_id, "level": course.level, "category": course.category,
            "total_stars": total_stars,
            "earned_stars": earned_stars,
            "completion_percentage": completion_percentage
        }

        enrolled_course_data = EnrolledCourseData(**course_data_dict)
        courses_with_progress.append(enrolled_course_data)
        enrolled_titles.append(course.title)

    recommendations = ai_service.get_course_recommendations(db, enrolled_titles)

    return StudentDashboardData(
        enrolled_courses=courses_with_progress,
        recommended_courses=recommendations
    )