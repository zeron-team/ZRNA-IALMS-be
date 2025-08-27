from typing import Optional
from pydantic import BaseModel
from enum import Enum

class ModuleContext(str, Enum):
    education = "education"
    health = "health"
    constructor = "constructor"
    developer_software = "developer_software"
    more = "more"

class ModuleSkillType(str, Enum):
    jr = "jr"
    semi_sr = "semi_sr"
    sr = "sr"

class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int
    content_data: Optional[str] = None
    has_example: bool = False
    context: Optional[ModuleContext] = None
    skill_type: Optional[ModuleSkillType] = None

class ModuleCreate(ModuleBase):
    course_id: int

class ModuleUpdate(ModuleBase):
    pass

class ModuleResponse(ModuleBase):
    id: int
    course_id: int
    status: Optional[str] = None  # Add status field
    is_locked: Optional[bool] = None # Add is_locked field

    class Config:
        from_attributes = True