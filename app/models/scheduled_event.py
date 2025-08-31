from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.user import User as UserSchema # Import User schema

class ScheduledEventBase(BaseModel):
    room_id: int
    title: str
    start_time: datetime
    end_time: datetime
    event_type: str # video_call, lecture, meeting

class ScheduledEventCreate(ScheduledEventBase):
    invited_user_ids: List[int] = []

class EventInvitationWithUser(BaseModel):
    id: int
    event_id: int
    user_id: int
    status: str # pending, accepted, rejected
    user: UserSchema # Include user details
    class Config:
        from_attributes = True

class ScheduledEvent(ScheduledEventBase):
    id: int
    creator_id: int
    invitation_status: Optional[str] = None # Added for invited users
    invitations: List[EventInvitationWithUser] = [] # List of all invitations

    class Config:
        from_attributes = True

class EventInvitationBase(BaseModel):
    event_id: int
    user_id: int
    status: str # pending, accepted, rejected

class EventInvitationCreate(EventInvitationBase):
    pass

class EventInvitation(EventInvitationBase):
    id: int

    class Config:
        from_attributes = True