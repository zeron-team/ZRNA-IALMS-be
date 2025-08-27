from sqlalchemy.orm import Session
from typing import Optional, Dict
from .. import db_models

def create_or_update_rating(
    db: Session,
    user_id: int,
    course_id: Optional[int],
    module_id: Optional[int],
    is_upvote: bool
) -> db_models.Rating:
    if course_id and module_id:
        raise ValueError("Cannot rate both a course and a module simultaneously.")
    if not course_id and not module_id:
        raise ValueError("Must provide either a course_id or a module_id.")

    query = db.query(db_models.Rating).filter(db_models.Rating.user_id == user_id)

    if course_id:
        query = query.filter(db_models.Rating.course_id == course_id)
    elif module_id:
        query = query.filter(db_models.Rating.module_id == module_id)

    rating = query.first()

    if rating:
        rating.is_upvote = is_upvote
    else:
        rating = db_models.Rating(
            user_id=user_id,
            course_id=course_id,
            module_id=module_id,
            is_upvote=is_upvote
        )
        db.add(rating)

    db.commit()
    db.refresh(rating)
    return rating

def get_rating_counts(
    db: Session,
    course_id: Optional[int] = None,
    module_id: Optional[int] = None
) -> Dict[str, int]:
    if course_id and module_id:
        raise ValueError("Cannot get counts for both a course and a module simultaneously.")
    if not course_id and not module_id:
        raise ValueError("Must provide either a course_id or a module_id.")

    query = db.query(db_models.Rating)

    if course_id:
        query = query.filter(db_models.Rating.course_id == course_id)
    elif module_id:
        query = query.filter(db_models.Rating.module_id == module_id)

    upvotes = query.filter(db_models.Rating.is_upvote == True).count()
    downvotes = query.filter(db_models.Rating.is_upvote == False).count()

    return {"upvotes": upvotes, "downvotes": downvotes}

def get_global_rating_counts(db: Session) -> Dict[str, int]:
    upvotes = db.query(db_models.Rating).filter(db_models.Rating.is_upvote == True).count()
    downvotes = db.query(db_models.Rating).filter(db_models.Rating.is_upvote == False).count()
    return {"upvotes": upvotes, "downvotes": downvotes}

def get_user_rating(
    db: Session,
    user_id: int,
    course_id: Optional[int] = None,
    module_id: Optional[int] = None
) -> Optional[bool]:
    if course_id and module_id:
        raise ValueError("Cannot get user rating for both a course and a module simultaneously.")
    if not course_id and not module_id:
        raise ValueError("Must provide either a course_id or a module_id.")

    query = db.query(db_models.Rating).filter(db_models.Rating.user_id == user_id)

    if course_id:
        query = query.filter(db_models.Rating.course_id == course_id)
    elif module_id:
        query = query.filter(db_models.Rating.module_id == module_id)

    rating = query.first()

    if rating:
        return rating.is_upvote
    return None