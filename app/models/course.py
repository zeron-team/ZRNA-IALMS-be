# backend/app/models/course.py

from pydantic import BaseModel
from typing import List, Optional

class CourseBaseForCategory(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    level: str
    status: str
    class Config:
        from_attributes = True

# --- CATEGORY ---
class Category(BaseModel):
    id: int
    name: str
    courses: List[CourseBaseForCategory] = []


    class Config:
        from_attributes = True



# --- MODULE ---
class Module(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order_index: int
    status: str = "not_started"
    course_id: int
    content_data: Optional[str] = None
    is_locked: bool = False
    diagram_mermaid_syntax: Optional[str] = None # New field
    class Config:
        from_attributes = True

# --- COURSE ---
class Course(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    instructor_id: Optional[int] = None
    level: str
    category: Category # <-- Usa directamente la clase 'Category'
    total_stars: int = 0
    earned_stars: int = 0
    creator_id: Optional[int] = None  # <-- Permite que sea nulo
    is_free: Optional[bool] = True
    price: Optional[float] = 0.0

    class Config:
        from_attributes = True

class CourseWithProgress(Course):
    completion_percentage: int = 0

class CourseDetail(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    creator_id: Optional[int] = None  # <-- Añade el creator_id aquí
    modules: List[Module] = []
    is_enrolled: bool = False
    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: int
    level: str
    is_free: Optional[bool] = True
    price: Optional[float] = 0.0

