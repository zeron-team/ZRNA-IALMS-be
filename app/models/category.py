# backend/app/models/category.py

from pydantic import BaseModel

class Category(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True