# backend/app/routers/enrollments.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.security import get_current_active_user
from app.models.user import User as UserSchema
from app.models.course import CourseWithProgress
from app.repositories import enrollment_repo, progress_repo, course_repo  # Importa course_repo
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
    course = course_repo.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")

    # Aquí puedes añadir la lógica de planes de pago si lo necesitas
    # if user_plan == "Gratuito" and course.price > 0:
    #     raise HTTPException(status_code=403, detail="Tu plan no permite acceso a este curso.")

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
    created_courses = course_repo.get_courses_created_by_user(db, user_id=current_user.id)

    all_my_courses = {course.id: course for course in enrolled_courses}
    for course in created_courses:
        if course.id not in all_my_courses:
            all_my_courses[course.id] = course

    courses_with_data = []
    for course in all_my_courses.values():
        total_modules = len(course.modules)
        completed_modules = progress_repo.get_completed_modules_count(db, current_user.id, course.id)
        percentage = round((completed_modules / total_modules) * 100) if total_modules > 0 else 0

        total, earned = course_logic.calculate_star_rating(db, course, current_user.id)

        # --- CORRECCIÓN: Construimos un diccionario primero ---
        course_data_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor_id": course.instructor_id,
            "level": course.level,
            "category": course.category,
            "total_stars": total,
            "earned_stars": earned,
            "completion_percentage": percentage
        }

        # Ahora creamos el objeto Pydantic desde el diccionario completo
        course_data = CourseWithProgress(**course_data_dict)
        courses_with_data.append(course_data)

    return courses_with_data