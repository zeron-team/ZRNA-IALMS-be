# backend/app/repositories/base.py
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.course import Course, CourseDetail

class ICourseRepository(ABC):
    @abstractmethod
    def get_all_courses(self) -> List[Course]:
        pass

    @abstractmethod
    def get_course_by_id(self, course_id: int) -> Optional[CourseDetail]:
        pass