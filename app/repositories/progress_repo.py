# backend/app/repositories/progress_repo.py
from sqlalchemy.orm import Session
from app import db_models


def mark_module_as_completed(db: Session, user_id: int, module_id: int):
    """Busca un registro de progreso y lo marca como 'completed'. Si no existe, lo crea."""
    progress = db.query(db_models.StudentProgress).filter_by(
        user_id=user_id, module_id=module_id
    ).first()

    if progress:
        progress.status = 'completed'
    else:
        progress = db_models.StudentProgress(
            user_id=user_id,
            module_id=module_id,
            status='completed'
        )
        db.add(progress)

    db.commit()
    return progress


def get_progress_for_course(db: Session, user_id: int, course_id: int):
    """Obtiene todos los registros de progreso de un usuario para un curso específico."""
    return db.query(db_models.StudentProgress).join(db_models.Module).filter(
        db_models.StudentProgress.user_id == user_id,
        db_models.Module.course_id == course_id
    ).all()

def get_completed_modules_count(db: Session, user_id: int, course_id: int) -> int:
    """Cuenta cuántos módulos de un curso ha completado un usuario."""
    return db.query(db_models.StudentProgress).join(db_models.Module).filter(
        db_models.StudentProgress.user_id == user_id,
        db_models.Module.course_id == course_id,
        db_models.StudentProgress.status == 'completed'
    ).count()