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
from app.security import get_current_active_user, instructor_required

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

    # --- LÓGICA DE VALIDACIÓN CORREGIDA ---
    is_enrolled = enrollment_repo.is_enrolled(db, user_id=current_user.id, course_id=db_module.course_id)
    is_instructor_or_admin = current_user.role.name in ['instructor', 'admin']

    # Permite el acceso si el usuario está inscrito O si es un instructor/admin
    if not is_enrolled and not is_instructor_or_admin:
        raise HTTPException(status_code=403, detail="Debes inscribirte en el curso para ver este módulo.")
    # ------------------------------------------

    return db_module

@router.post("/{module_id}/generate-content", response_model=ModuleSchema)
async def generate_content_for_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service),
    current_user: UserSchema = Depends(instructor_required)
):
    """
    Genera y guarda el contenido detallado para un módulo usando IA.
    Requiere rol de instructor o admin.
    """
    updated_module = await service.generate_and_save_content(module_id)
    if not updated_module:
        raise HTTPException(status_code=500, detail="Failed to generate content")
    return updated_module