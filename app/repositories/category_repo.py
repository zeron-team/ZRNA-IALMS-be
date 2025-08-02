# backend/app/repositories/category_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models

def get_categories(db: Session):
    """Obtiene todas las categorías de la base de datos."""
    return db.query(db_models.Category).all()

def get_categories_with_courses(db: Session):
    """Obtiene todas las categorías, cargando los cursos publicados de cada una."""
    return db.query(db_models.Category).options(
        joinedload(db_models.Category.courses)
    ).all()