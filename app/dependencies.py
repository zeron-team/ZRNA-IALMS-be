from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import SessionLocal
from app.services.course_service import CourseService
from app.services.module_service import ModuleService

# 1. Se define PRIMERO la dependencia de base de datos, ya que las otras la usan.
def get_db():
    """
    Dependencia de FastAPI para crear y cerrar una sesión de base de datos por petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Ahora se definen las dependencias de los servicios, que usan get_db.
def get_course_service(db: Session = Depends(get_db)) -> CourseService:
    """Dependencia para obtener el servicio de cursos."""
    return CourseService(db)

def get_module_service(db: Session = Depends(get_db)) -> ModuleService:
    """Dependencia para obtener el servicio de módulos."""
    return ModuleService(db)