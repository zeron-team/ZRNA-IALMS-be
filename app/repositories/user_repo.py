from sqlalchemy.orm import Session, joinedload
from app import db_models
from app.models import user as user_schemas
from app.core.hashing import get_password_hash


def get_user_by_id(db: Session, user_id: int):
    """Obtiene un usuario por su ID, incluyendo su perfil."""
    return db.query(db_models.User).options(joinedload(db_models.User.profile)).filter(
        db_models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """Obtiene un usuario por su nombre de usuario."""
    return db.query(db_models.User).filter(db_models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista de todos los usuarios, incluyendo sus perfiles."""
    return db.query(db_models.User).options(joinedload(db_models.User.profile)).offset(skip).limit(limit).all()


def create_user(db: Session, user: user_schemas.UserCreate):
    """Crea un nuevo usuario y su perfil vacío asociado."""
    hashed_password = get_password_hash(user.password)
    db_user = db_models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role_id=user.role_id
    )
    # Crea un perfil vacío al mismo tiempo
    db_user.profile = db_models.UserProfile()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: user_schemas.UserUpdate):
    """Actualiza los datos de un usuario (email, rol y perfil)."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    if "email" in update_data:
        db_user.email = update_data["email"]
    if "role_id" in update_data:
        db_user.role_id = update_data["role_id"]
    if "profile" in update_data and db_user.profile:
        profile_data = update_data["profile"]
        for key, value in profile_data.items():
            setattr(db_user.profile, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Elimina un usuario de la base de datos."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True