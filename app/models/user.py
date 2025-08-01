from pydantic import BaseModel, EmailStr
from typing import Optional


# --- Modelo base del Usuario ---
# Este es el modelo que faltaba. Representa los datos de un usuario
# que son seguros para usar dentro de la aplicación y devolver en la API.
class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str

    class Config:
        from_attributes = True # En Pydantic v1 era orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = 'student'

# --- Modelo para la Base de Datos ---
# Este modelo hereda de User y añade el campo `hashed_password`.
# Solo se debe usar internamente para la lógica de autenticación.
class UserInDB(User):
    hashed_password: str


# --- Modelo para el Token ---
# Define la estructura de la respuesta del token JWT.
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

# --- Perfil ---
class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None

class UserProfile(UserProfileBase):
    class Config:
        from_attributes = True

# --- Rol ---
class Role(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

# --- Usuario ---
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role_id: int = 1

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    profile: Optional[UserProfileBase] = None
    role_id: Optional[int] = None

class User(UserBase):
    id: int
    role: Role
    profile: Optional[UserProfile] = None
    class Config:
        from_attributes = True