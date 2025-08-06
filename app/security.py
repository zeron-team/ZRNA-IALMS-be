# backend/app/security.py

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.hashing import verify_password
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.dependencies import get_db
# --- LÍNEA AÑADIDA ---
from app.repositories import user_repo, course_repo, module_repo
from app.models.user import User as PydanticUser

# --- Configuración ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# --- Funciones de Token JWT ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- Funciones de Autenticación y Dependencias ---
def authenticate_user(db: Session, username: str, password: str):
    user = user_repo.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_repo.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: PydanticUser = Depends(get_current_user)):
    return current_user


# --- ESTA ES LA FUNCIÓN CORREGIDA ---
async def instructor_required(current_user: PydanticUser = Depends(get_current_active_user)):
    """
    Dependencia que verifica si el rol del usuario es 'instructor' o 'admin'.
    """
    # Esta línea permite el acceso a ambos roles
    if current_user.role.name not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol de instructor o admin."
        )
    return current_user

async def admin_required(current_user: PydanticUser = Depends(get_current_active_user)):
    """
    Dependencia que verifica si el rol del usuario actual es 'admin'.
    """
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol de administrador."
        )
    return current_user

async def is_owner_or_instructor(
    user_id: int,
    current_user: PydanticUser = Depends(get_current_active_user)
):
    """
    Verifica si el usuario actual es el dueño del perfil que intenta editar
    o si es un instructor/admin.
    """
    if current_user.id == user_id or current_user.role.name in ['instructor', 'admin']:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permiso para realizar esta acción."
    )

async def can_edit_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
):
    """Verifica si el usuario actual puede editar un curso (por rol o por ser creador)."""
    course = course_repo.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    is_admin_or_instructor = current_user.role.name in ['admin', 'instructor']
    is_creator = course.creator_id == current_user.id

    if not is_admin_or_instructor and not is_creator:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este curso.")
    return current_user

async def can_edit_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
):
    """Verifica si el usuario actual puede editar un módulo."""
    module = module_repo.get_module_by_id(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    course = module.course
    is_admin_or_instructor = current_user.role.name in ['admin', 'instructor']
    is_creator = course.creator_id == current_user.id

    if not is_admin_or_instructor and not is_creator:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este módulo.")
    return current_user