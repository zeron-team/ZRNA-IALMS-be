# backend/app/routers/courses.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

# --- Modelos Pydantic ---
from app.models.course import Course, CourseCreate, CourseDetail, Module
from app.models.user import User as PydanticUser

# --- Dependencias, Repositorios y Servicios ---
from app.dependencies import get_db, get_course_service
from app.services.course_service import CourseService
from app.security import instructor_required, get_current_active_user
from app.repositories import course_repo, progress_repo

from app.logic import course_logic
from app.models.user import User as UserSchema

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


@router.get("/", response_model=List[Course])
async def read_courses(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    all_courses = course_repo.get_all_courses(db)
    # Para cada curso, calculamos y añadimos las estrellas
    for course in all_courses:
        course.total_stars, course.earned_stars = course_logic.calculate_star_rating(
            db, course, current_user.id
        )
    return all_courses


@router.get("/{course_id}", response_model=CourseDetail)
async def read_course_detail(
        course_id: int,
        db: Session = Depends(get_db),
        current_user: PydanticUser = Depends(get_current_active_user)
):
    db_course = course_repo.get_course_by_id(db, course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    user_progress_map = {
        p.module_id: p.status
        for p in progress_repo.get_progress_for_course(db, current_user.id, course_id)
    }

    modules_with_status = []
    previous_module_completed = True  # El primer módulo siempre está desbloqueado

    for module in sorted(db_course.modules, key=lambda m: m.order_index):
        status = user_progress_map.get(module.id, 'not_started')

        # El módulo actual está bloqueado si el anterior no fue completado
        is_locked = not previous_module_completed

        # Prepara la "llave" para la siguiente iteración del bucle
        if status == 'completed':
            previous_module_completed = True
        else:
            previous_module_completed = False

        module_schema_data = {
            "id": module.id, "title": module.title, "description": module.description,
            "order_index": module.order_index, "content_data": module.content_data,
            "course_id": module.course_id, "status": status, "is_locked": is_locked
        }
        modules_with_status.append(module_schema_data)

    return CourseDetail(
        id=db_course.id,
        title=db_course.title,
        description=db_course.description,
        modules=modules_with_status
    )


@router.get("/{course_id}/summary", response_model=str)
async def get_course_summary(
        course_id: int,
        service: CourseService = Depends(get_course_service)
):
    summary = await service.generate_course_summary(course_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return summary


@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(
        course: CourseCreate,
        service: CourseService = Depends(get_course_service),
        current_user: PydanticUser = Depends(instructor_required)
):
    return await service.create_new_course(course, instructor_id=current_user.id)


@router.put("/{course_id}", response_model=Course)
async def update_course(
        course_id: int,
        course_update: CourseCreate,
        service: CourseService = Depends(get_course_service),
        current_user: PydanticUser = Depends(instructor_required)
):
    updated = await service.update_existing_course(course_id, course_update, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    return updated


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
        course_id: int,
        service: CourseService = Depends(get_course_service),
        current_user: PydanticUser = Depends(instructor_required)
):
    success = await service.delete_existing_course(course_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    return


@router.post("/{course_id}/generate-curriculum", response_model=List[Module])
async def generate_course_curriculum(
        course_id: int,
        service: CourseService = Depends(get_course_service),
        current_user: PydanticUser = Depends(instructor_required)
):
    modules = await service.generate_and_save_curriculum(course_id)
    if modules is None:
        raise HTTPException(status_code=500, detail="No se pudo generar la currícula.")
    return modules


@router.post("/modules/{module_id}/complete", status_code=status.HTTP_200_OK)
async def complete_module(
        module_id: int,
        service: CourseService = Depends(get_course_service),
        current_user: PydanticUser = Depends(get_current_active_user)
):
    await service.mark_module_completed(current_user.id, module_id)
    return {"message": "Module marked as completed."}