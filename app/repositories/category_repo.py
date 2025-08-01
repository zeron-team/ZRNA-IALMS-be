# backend/app/repositories/category_repo.py

from sqlalchemy.orm import Session
from app import db_models

def get_categories(db: Session):
    """Obtiene todas las categorías de la base de datos."""
    return db.query(db_models.Category).all()