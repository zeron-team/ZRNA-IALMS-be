# backend/app/repositories/learning_path_repo.py

from sqlalchemy.orm import Session, joinedload
from app import db_models
from app.models.learning_path import LearningPathCreate

def get_learning_paths(db: Session):
    return db.query(db_models.LearningPath).all()

def get_learning_path_by_id(db: Session, path_id: int):
    return db.query(db_models.LearningPath).options(
        joinedload(db_models.LearningPath.courses)
        .joinedload(db_models.LearningPathCourse.course)
        .joinedload(db_models.Course.category)
    ).filter(db_models.LearningPath.id == path_id).first()

def create_learning_path(db: Session, path: LearningPathCreate):
    db_path = db_models.LearningPath(**path.model_dump())
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    return db_path

def delete_learning_path(db: Session, path_id: int) -> bool:
    db_path = db.query(db_models.LearningPath).filter(db_models.LearningPath.id == path_id).first()
    if db_path:
        db.delete(db_path)
        db.commit()
        return True
    return False

def add_course_to_path(db: Session, path_id: int, course_id: int, step: int):
    db_assoc = db_models.LearningPathCourse(path_id=path_id, course_id=course_id, step=step)
    db.add(db_assoc)
    db.commit()
    db.refresh(db_assoc)
    return db_assoc