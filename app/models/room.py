# backend/app/models/room.py

from pydantic import BaseModel
from typing import List, Optional
from .user import User as UserSchema
from .course import Course as CourseSchema

class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    instructor_id: int
    join_code: str
    courses: List[CourseSchema] = []
    members: List[UserSchema] = []
    class Config:
        from_attributes = True