# backend/app/routers/auth.py

import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr # <-- Se añade la importación

from app.dependencies import get_db
from app.security import authenticate_user, create_access_token
from app.models.user import UserCreate, Token
from app.services import email_service
from app.repositories import user_repo

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
class RegisterResponse(BaseModel):
    message: str
    email: EmailStr

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    user_repo.update_user_last_login(db, user_id=user.id)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Crea un usuario inactivo y le envía un correo de verificación."""
    existing_user = user_repo.get_user_by_email(db, email=user_data.email)

    if existing_user:
        # Por seguridad, no revelamos que el email ya existe, pero podemos reenviar el correo
        if not existing_user.is_active and existing_user.verification_token:
            email_service.send_verification_email(existing_user.email, existing_user.verification_token)
        return {"message": "Correo de verificación enviado.", "email": existing_user.email}

    user = user_repo.create_user(db, user_data)
    if user and user.verification_token:
        email_service.send_verification_email(user.email, user.verification_token)

    return {"message": "Correo de verificación enviado.", "email": user.email}

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Activa una cuenta de usuario a través del token de verificación."""
    user = user_repo.activate_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Token de verificación inválido o expirado.")
    return {"message": "Cuenta verificada con éxito. Ya puedes iniciar sesión."}

# (Aquí podrías añadir en el futuro la lógica para "Olvidé mi contraseña")