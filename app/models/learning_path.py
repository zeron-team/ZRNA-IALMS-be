# backend/app/models/learning_path.py

from pydantic import BaseModel
from typing import List, Optional
# CORRECCIÓN: Importa 'Course' y 'Category' desde 'app.models.course'
from .course import Course as CourseSchema, Category as CategorySchema

class LearningPathBase(BaseModel):
    title: str
    description: Optional[str] = None

class LearningPathCreate(LearningPathBase):
    pass

class LearningPath(LearningPathBase):
    id: int
    class Config:
        from_attributes = True

class LearningPathCourse(CourseSchema):
    step: int
    user_status: str

class LearningPathDetail(LearningPath):
    courses: List[LearningPathCourse] = []

class PathCourseCreate(BaseModel):
    course_id: int
    step: int