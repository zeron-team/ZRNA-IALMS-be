from pydantic import BaseModel  # <-- Añade esta línea
from typing import Optional

class Role(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True