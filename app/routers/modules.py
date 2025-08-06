# backend/app/routers/modules.py

# --- FastAPI & SQLAlchemy ---
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# --- Modelos Pydantic ---
from app.models.course import Module as ModuleSchema
from app.models.user import User as UserSchema

# --- Dependencias, Repositorios y Servicios ---
from app.dependencies import get_db, get_module_service
from app.repositories import module_repo, enrollment_repo
from app.services.module_service import ModuleService
from app.security import instructor_required, get_current_active_user, can_edit_module # <-- Importa la nueva regla

router = APIRouter(
    prefix="/modules",
    tags=["Modules"]
)

@router.get("/{module_id}", response_model=ModuleSchema)
def read_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    db_module = module_repo.get_module_by_id(db, module_id=module_id)
    if db_module is None:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    # Obtenemos el curso al que pertenece el módulo
    db_course = db_module.course

    # --- LÓGICA DE PERMISOS CORREGIDA ---
    is_enrolled = enrollment_repo.is_enrolled(db, user_id=current_user.id, course_id=db_course.id)
    is_instructor_or_admin = current_user.role.name in ['instructor', 'admin']
    is_creator = db_course.creator_id == current_user.id

    # Permite el acceso si se cumple CUALQUIERA de estas condiciones
    if not is_enrolled and not is_instructor_or_admin and not is_creator:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este módulo.")
    # ------------------------------------------

    return db_module

@router.post("/{module_id}/generate-content", response_model=ModuleSchema)
async def generate_content_for_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
    # Reemplaza 'instructor_required' con la nueva dependencia
    current_user: UserSchema = Depends(can_edit_module)
):
    """Genera y guarda el contenido detallado para un módulo usando IA."""
    updated_module = await service.generate_and_save_content(module_id)
    if not updated_module:
        raise HTTPException(status_code=500, detail="Failed to generate content")
    return updated_module