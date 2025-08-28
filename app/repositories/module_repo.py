from sqlalchemy.orm import Session
from app import db_models

def get_module_by_id(db: Session, module_id: int):
    """
    Busca y devuelve un módulo por su ID único.

    Args:
        db (Session): La sesión de la base de datos.
        module_id (int): El ID del módulo a buscar.

    Returns:
        db_models.Module | None: El objeto del módulo si se encuentra, de lo contrario None.
    """
    return db.query(db_models.Module).filter(db_models.Module.id == module_id).first()

def update_module_content(db: Session, module_id: int, content: str):
    """
    Encuentra un módulo por su ID y actualiza su campo de contenido (content_data).

    Args:
        db (Session): La sesión de la base de datos.
        module_id (int): El ID del módulo a actualizar.
        content (str): El nuevo contenido generado por la IA.

    Returns:
        db_models.Module | None: El objeto del módulo actualizado si se encuentra, de lo contrario None.
    """
    db_module = get_module_by_id(db, module_id)
    if db_module:
        db_module.content_data = content
        db.commit()
        db.refresh(db_module)
    return db_module

def update_module_audio(db: Session, module_id: int, audio_path: str):
    """
    Encuentra un módulo por su ID y actualiza su campo de audio (content_audio_url).

    Args:
        db (Session): La sesión de la base de datos.
        module_id (int): El ID del módulo a actualizar.
        audio_path (str): La ruta al archivo de audio generado.

    Returns:
        db_models.Module | None: El objeto del módulo actualizado si se encuentra, de lo contrario None.
    """
    db_module = get_module_by_id(db, module_id)
    if db_module:
        db_module.content_audio_url = audio_path
        db.commit()
        db.refresh(db_module)
    return db_module