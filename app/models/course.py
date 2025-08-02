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
    class Config:
        from_attributes = True

# --- COURSE ---
class Course(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    instructor_id: int
    level: str
    category: Category
    total_stars: int = 0
    earned_stars: int = 0
    class Config:
        from_attributes = True

class CourseWithProgress(Course):
    completion_percentage: int = 0

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

