from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.repositories import role_repo
from app.models.role import Role as RoleSchema
from app.security import instructor_required
from app.models.user import User as UserSchema

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.get("/", response_model=List[RoleSchema])
def read_all_roles(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(instructor_required) 
):
    """Obtiene una lista de todos los roles disponibles."""
    return role_repo.get_roles(db)