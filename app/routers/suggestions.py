from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import difflib # Re-added this import
from app.security import get_current_active_user
from app.models.user import User as PydanticUser # Assuming User model is in app.models.user

from .. import db_models
from ..dependencies import get_db

router = APIRouter()

# Pydantic models
class CourseSuggestionBase(BaseModel):
    topic: str

class CourseSuggestionCreate(CourseSuggestionBase):
    pass

class CourseSuggestion(BaseModel):
    id: int
    topic: str # Added this line
    votes: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

# API Endpoints
@router.post("/suggestions", response_model=CourseSuggestion, status_code=status.HTTP_201_CREATED)
def create_course_suggestion(suggestion: CourseSuggestionCreate, db: Session = Depends(get_db)):
    print(f"Received new course suggestion: {suggestion.topic}")

    # Merging logic: Check for similar existing suggestions
    all_suggestions = db.query(db_models.CourseSuggestion).all()
    new_topic_lower = suggestion.topic.lower()
    
    # Define a similarity cutoff for merging (e.g., 0.8 for strong similarity)
    MERGE_CUTOFF = 0.8

    for existing_sugg in all_suggestions:
        # Use SequenceMatcher to calculate similarity ratio
        similarity_ratio = difflib.SequenceMatcher(None, new_topic_lower, existing_sugg.topic.lower()).ratio()
        
        if similarity_ratio >= MERGE_CUTOFF:
            print(f"Merging '{suggestion.topic}' with existing suggestion '{existing_sugg.topic}' (Similarity: {similarity_ratio:.2f})")
            existing_sugg.votes += 1
            db.commit()
            db.refresh(existing_sugg)
            return existing_sugg # Return the merged suggestion

    # If no similar suggestion found, create a new one
    db_suggestion = db_models.CourseSuggestion(topic=suggestion.topic)
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion

@router.get("/suggestions", response_model=List[CourseSuggestion])
def get_course_suggestions(db: Session = Depends(get_db)):
    suggestions = db.query(db_models.CourseSuggestion).order_by(db_models.CourseSuggestion.votes.desc()).all()
    return suggestions

@router.post("/suggestions/{suggestion_id}/vote", response_model=CourseSuggestion)
def vote_for_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    db_suggestion = db.query(db_models.CourseSuggestion).filter(db_models.CourseSuggestion.id == suggestion_id).first()
    if not db_suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found.")

    db_suggestion.votes += 1
    db.commit()
    db.refresh(db_suggestion)

    # Placeholder for AI course creation trigger
    if db_suggestion.votes >= 100:
        print(f"AI should create a course for: {db_suggestion.topic}")
        # In a real application, you would trigger an AI service here
        db_suggestion.status = "course_created"
        db.commit()
        db.refresh(db_suggestion)

    return db_suggestion

@router.get("/suggestions/search", response_model=List[CourseSuggestion])
def search_course_suggestions(query: str, db: Session = Depends(get_db)):
    query_lower = query.lower()
    
    # Filter suggestions where the topic (lowercase) contains the query (lowercase)
    matched_suggestions = [
        s for s in db.query(db_models.CourseSuggestion).all() 
        if query_lower in s.topic.lower()
    ]
    
    return matched_suggestions

