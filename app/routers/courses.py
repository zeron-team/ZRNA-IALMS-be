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
from app.security import instructor_required, get_current_active_user, can_edit_course
from app.repositories import course_repo, progress_repo

from app.logic import course_logic
from app.models.user import User as UserSchema

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


@router.get("/", response_model=List[Course])
def read_courses(
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_active_user)
):
    """Obtiene todos los cursos publicados y calcula las estrellas para el usuario actual."""
    all_courses = course_repo.get_published_courses(db)
    for course in all_courses:
        course.total_stars, course.earned_stars = course_logic.calculate_star_rating(
            db, course, current_user.id
        )
    return all_courses


@router.get("/{course_id}", response_model=CourseDetail)
def read_course_detail(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    db_course = course_repo.get_course_by_id(db, course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")

    # ... (lógica de permisos para borradores)

    user_progress_map = {p.module_id: p.status for p in
                         progress_repo.get_progress_for_course(db, current_user.id, course_id)}

    modules_with_status = []
    previous_module_completed = True
    for module in sorted(db_course.modules, key=lambda m: m.order_index):
        status = user_progress_map.get(module.id, 'not_started')
        is_locked = not previous_module_completed

        if current_user.role.name in ['instructor', 'admin']:
            is_locked = False

        if status == 'completed':
            previous_module_completed = True
        else:
            previous_module_completed = False

        module_data = Module.model_validate(module)
        module_data.status = status
        module_data.is_locked = is_locked
        modules_with_status.append(module_data)

    # --- CORRECCIÓN AQUÍ ---
    # Construimos un diccionario con los datos del curso y la lista de módulos ya procesada
    course_detail_data = {
        "id": db_course.id,
        "title": db_course.title,
        "description": db_course.description,
        "modules": modules_with_status
    }
    # La forma más limpia de construir la respuesta
    course_data = CourseDetail.model_validate(db_course)
    course_data.modules = modules_with_status  # Asigna la lista de módulos procesada

    return course_data


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
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Crea un nuevo curso. Los estudiantes tienen un límite."""
    if current_user.role.name == 'student':
        if course_repo.count_courses_created_by_user(db, user_id=current_user.id) >= 2:
            raise HTTPException(status_code=403, detail="Límite de creación alcanzado.")
        # Llama a una función específica para estudiantes
        return course_repo.create_student_course(db, course=course, creator_id=current_user.id)
    else:
        # Llama a la función para instructores/admins
        return course_repo.create_instructor_course(db, course=course, instructor_id=current_user.id)


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
    # --- PARÁMETROS REORDENADOS ---
    # 1. Parámetros sin valor por defecto (vienen de la ruta)
    course_id: int,
    # 2. Parámetros con valor por defecto (vienen de la inyección de dependencias)
    current_user: UserSchema = Depends(can_edit_course),
    service: CourseService = Depends(get_course_service)
):
    """
    Genera una currícula de módulos para un curso.
    """
    modules = await service.generate_and_save_curriculum(course_id=course_id)
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


