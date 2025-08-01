from sqlalchemy.orm import Session
from app import db_models

def get_module_by_id(db: Session, module_id: int):
    return db.query(db_models.Module).filter(db_models.Module.id == module_id).first()

def update_module_content(db: Session, module_id: int, content: str):
    """Encuentra un módulo y actualiza su campo de contenido."""
    db_module = get_module_by_id(db, module_id)
    if db_module:
        db_module.content_data = content
        db.commit()
        db.refresh(db_module)
    return db_module