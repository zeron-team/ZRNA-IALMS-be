# backend/app/routers/categories.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.repositories import category_repo
from app.models.category import Category as CategorySchema

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.get("/", response_model=List[CategorySchema])
def read_all_categories(db: Session = Depends(get_db)):
    """Obtiene una lista de todas las categorías de cursos."""
    return category_repo.get_categories(db)