from sqlalchemy.orm import Session
from app import db_models

def get_roles(db: Session):
    """Obtiene todos los roles de la base de datos."""
    return db.query(db_models.Role).all()