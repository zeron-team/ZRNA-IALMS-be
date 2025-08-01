# backend/app/models/dashboard.py

from pydantic import BaseModel
from typing import List
from .course import Course as CourseSchema

class EnrolledCourseData(CourseSchema):
    completion_percentage: int
    total_stars: int  # <-- Campo añadido
    earned_stars: int  # <-- Campo añadido

class StudentDashboardData(BaseModel):
    enrolled_courses: List[EnrolledCourseData]
    recommended_courses: List[CourseSchema]