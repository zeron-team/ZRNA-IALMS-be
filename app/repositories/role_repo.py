from sqlalchemy.orm import Session
from app import db_models

def get_roles(db: Session):
    """Obtiene todos los roles de la base de datos."""
    return db.query(db_models.Role).all()

def get_roles(db: Session):
    """Obtiene una lista de todos los roles."""
    return db.query(db_models.Role).all()

# --- ESTA ES LA FUNCIÓN QUE FALTA ---
def get_role_by_name(db: Session, name: str):
    """Busca un rol por su nombre."""
    return db.query(db_models.Role).filter(db_models.Role.name == name).first()