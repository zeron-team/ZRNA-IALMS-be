print("--- PRUEBA DE CARGA DEFINITIVA PARA ROUTER DE USUARIOS ---")

# --- FastAPI & SQLAlchemy ---

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# --- Modelos (Schemas) ---
from app.models.user import User as UserSchema, UserCreate, UserUpdate
from app.models.course import Course as CourseSchema
from app.models.user import User as PydanticUser, UserCreate

# --- Repositorio y Dependencias ---
from app.repositories import user_repo
from app.dependencies import get_db
from app.security import get_current_active_user, instructor_required
from app.services.course_service import CourseService

# --- Dependencias y Seguridad ---
from app.dependencies import get_db, get_course_service
from app.security import get_current_active_user, instructor_required

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# --- Ruta de Registro / Creación de Usuario ---
@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario."""
    if user_repo.get_user_by_username(db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_repo.create_user(db=db, user=user)

# --- Ruta para obtener el usuario logueado ---
@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserSchema = Depends(get_current_active_user)):
    """Obtiene los datos del usuario actualmente autenticado."""
    return current_user

# --- Rutas Administrativas ---

@router.get("/", response_model=List[UserSchema])
def read_all_users(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    """Obtiene una lista de todos los usuarios."""
    return user_repo.get_users(db)

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(instructor_required)
):
    """Obtiene los detalles de un usuario específico."""
    db_user = user_repo.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserSchema)
def update_existing_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    """Actualiza la información y/o rol de un usuario."""
    updated_user = user_repo.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required)
):
    """Elimina un usuario."""
    if not user_repo.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return

@router.get("/me/courses", response_model=List[CourseSchema])
async def read_my_courses(
    current_user: PydanticUser = Depends(get_current_active_user),
    service: CourseService = Depends(get_course_service)
):
    """Obtiene todos los cursos del instructor o admin actualmente logueado."""
    if current_user.role.name not in ['instructor', 'admin']:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return await service.find_courses_by_instructor(current_user.id)