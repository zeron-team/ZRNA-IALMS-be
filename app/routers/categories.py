# backend/app/routers/categories.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.repositories import category_repo
# CORRECCIÓN: Importa el schema correcto desde 'app.models.course'
from app.models.course import Category as CategorySchema

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.get("/", response_model=List[CategorySchema])
def read_all_categories(db: Session = Depends(get_db)): # <-- Se elimina la dependencia de 'current_user'
    """Obtiene una lista de todas las categorías de cursos."""
    return category_repo.get_categories(db)

@router.get("/with-courses", response_model=List[CategorySchema])
def read_categories_with_courses(db: Session = Depends(get_db)):
    """Obtiene una lista de todas las categorías con sus cursos asociados."""
    categories = category_repo.get_categories_with_courses(db)
    # Filtramos para mostrar solo cursos publicados en la landing
    for category in categories:
        category.courses = [course for course in category.courses if course.status == 'published']
    return categories