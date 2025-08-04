#backend/app/models/admin.py

from pydantic import BaseModel
from typing import List
from .user import User as UserSchema # Importa el schema base del usuario

class DashboardStats(BaseModel):
    total_users: int
    total_courses: int
    total_enrollments: int
    total_categories: int

class CourseEnrollmentStats(BaseModel):
    id: int
    title: str
    enrollment_count: int

class AdminDashboardData(BaseModel):
    total_users: int
    total_courses: int
    total_enrollments: int
    total_categories: int

class CourseWithEnrollments(BaseModel):
    id: int
    title: str
    enrolled_students: List[UserSchema] = []

    class Config:
        from_attributes = True
