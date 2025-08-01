# backend/app/models/course.py

from pydantic import BaseModel
from typing import List, Optional
from .category import Category as CategorySchema

class Module(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order_index: int
    status: str = "not_started"
    course_id: int
    content_data: Optional[str] = None
    is_locked: bool = False

    class Config:
        from_attributes = True

class CourseDetail(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    modules: List[Module] = []

    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: int
    level: str

class Course(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    instructor_id: int
    level: str
    category: CategorySchema
    total_stars: int = 3
    earned_stars: int = 0
    #completion_percentage: int = 0

    class Config:
        from_attributes = True

class CourseWithProgress(Course):
    completion_percentage: int = 0
    total_stars: int = 3  # <-- Campo añadido
    earned_stars: int = 0  # <-- Campo añadido