from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db
from app.security import get_current_active_user
from app.models.user import User as UserSchema
from app.models.rating import RatingCreate, RatingResponse, RatingCounts
from app.repositories import rating_repo

router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"]
)

@router.post("/course/{course_id}", response_model=RatingResponse)
def rate_course(
    course_id: int,
    rating_in: RatingCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    if rating_in.module_id is not None:
        raise HTTPException(status_code=400, detail="Cannot provide module_id when rating a course.")
    try:
        rating = rating_repo.create_or_update_rating(
            db, user_id=current_user.id, course_id=course_id, module_id=None, is_upvote=rating_in.is_upvote
        )
        return rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/module/{module_id}", response_model=RatingResponse)
def rate_module(
    module_id: int,
    rating_in: RatingCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    if rating_in.course_id is not None:
        raise HTTPException(status_code=400, detail="Cannot provide course_id when rating a module.")
    try:
        rating = rating_repo.create_or_update_rating(
            db, user_id=current_user.id, course_id=None, module_id=module_id, is_upvote=rating_in.is_upvote
        )
        return rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/course/{course_id}", response_model=RatingCounts)
def get_course_rating_counts(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        counts = rating_repo.get_rating_counts(db, course_id=course_id, module_id=None)
        user_rating = rating_repo.get_user_rating(db, user_id=current_user.id, course_id=course_id, module_id=None)
        return RatingCounts(**counts, user_rating=user_rating)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/module/{module_id}", response_model=RatingCounts)
def get_module_rating_counts(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    try:
        counts = rating_repo.get_rating_counts(db, course_id=None, module_id=module_id)
        user_rating = rating_repo.get_user_rating(db, user_id=current_user.id, course_id=None, module_id=module_id)
        return RatingCounts(**counts, user_rating=user_rating)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/global-counts", response_model=RatingCounts)
def get_global_rating_counts_api(
    db: Session = Depends(get_db)
):
    try:
        counts = rating_repo.get_global_rating_counts(db)
        return RatingCounts(**counts, user_rating=None) # user_rating is not applicable for global counts
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/course/{course_id}/public", response_model=RatingCounts)
def get_course_rating_counts_public(
    course_id: int,
    db: Session = Depends(get_db)
):
    try:
        counts = rating_repo.get_rating_counts(db, course_id=course_id, module_id=None)
        return RatingCounts(**counts, user_rating=None) # user_rating is not applicable for public counts
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
