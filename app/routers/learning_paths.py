# backend/app/routers/learning_paths.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.repositories import learning_path_repo, progress_repo
from app.models.learning_path import (
    LearningPath as LearningPathSchema,
    LearningPathDetail,
    LearningPathCourse,
    LearningPathCreate,
    PathCourseCreate
)
from app.models.user import User as UserSchema
from app.models.course import Course as CourseSchema
from app.security import get_current_active_user, instructor_required
from app.services import ai_service

router = APIRouter(
    prefix="/learning-paths",
    tags=["Learning Paths"]
)


@router.get("/", response_model=List[LearningPathSchema])
def read_all_learning_paths(db: Session = Depends(get_db)):
    return learning_path_repo.get_learning_paths(db)


@router.get("/{path_id}", response_model=LearningPathDetail)
def read_learning_path_details(
        path_id: int,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_active_user)
):
    db_path = learning_path_repo.get_learning_path_by_id(db, path_id)
    if not db_path:
        raise HTTPException(status_code=404, detail="Ruta no encontrada.")

    enrolled_course_ids = {e.course_id for e in current_user.enrollments}

    courses_in_path = []
    existing_titles = []
    sorted_associations = sorted(db_path.courses, key=lambda assoc: assoc.step)

    for assoc in sorted_associations:
        course = assoc.course
        user_status = "no_inscrito"
        if course.status == 'draft':
            user_status = 'en_desarrollo'
        elif course.id in enrolled_course_ids:
            completed_modules = progress_repo.get_completed_modules_count(db, current_user.id, course.id)
            total_modules = len(course.modules)
            user_status = 'terminado' if total_modules > 0 and completed_modules == total_modules else 'cursando'

        # Corrección del bug: Usar model_validate en lugar de __dict__
        course_schema = CourseSchema.model_validate(course)
        course_with_status = LearningPathCourse(
            **course_schema.model_dump(),
            step=assoc.step,
            user_status=user_status
        )
        courses_in_path.append(course_with_status)
        existing_titles.append(course.title)

    suggested_titles = ai_service.suggest_missing_courses_for_path(db_path.title, existing_titles)

    next_step = (courses_in_path[-1].step + 1) if courses_in_path else 1
    for i, title in enumerate(suggested_titles):
        missing_course = LearningPathCourse(
            id=-(i + 1), title=title, description="Sugerencia de la IA.",
            instructor_id=-1, level='basico',
            category={'id': -1, 'name': 'Sugerencia IA'},
            step=next_step + i, user_status="missing"
        )
        courses_in_path.append(missing_course)

    return LearningPathDetail(
        id=db_path.id, title=db_path.title,
        description=db_path.description, courses=courses_in_path
    )


# --- Endpoints del ABM ---

@router.post("/", response_model=LearningPathSchema, status_code=status.HTTP_201_CREATED)
def create_learning_path(
        path_data: LearningPathCreate,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(instructor_required)
):
    return learning_path_repo.create_learning_path(db=db, path=path_data)


@router.post("/{path_id}/courses", status_code=status.HTTP_201_CREATED)
def add_course_to_learning_path(
        path_id: int,
        path_course: PathCourseCreate,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(instructor_required)
):
    """Añade un curso existente a una ruta de conocimiento en un paso específico."""
    return learning_path_repo.add_course_to_path(
        db, path_id, path_course.course_id, path_course.step
    )


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_learning_path(
        path_id: int,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(instructor_required)
):
    """Elimina una ruta de conocimiento."""
    if not learning_path_repo.delete_learning_path(db, path_id):
        raise HTTPException(status_code=404, detail="Ruta no encontrada.")
    return