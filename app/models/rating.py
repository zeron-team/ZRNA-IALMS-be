from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class RatingBase(BaseModel):
    is_upvote: bool

class RatingCreate(RatingBase):
    course_id: Optional[int] = None
    module_id: Optional[int] = None

class RatingResponse(RatingBase):
    id: int
    user_id: int
    course_id: Optional[int] = None
    module_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RatingCounts(BaseModel):
    upvotes: int
    downvotes: int
    user_rating: Optional[bool] = None # True for upvote, False for downvote, None if not rated