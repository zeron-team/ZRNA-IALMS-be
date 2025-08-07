# backend/app/models/notification.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Notification(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    link_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True