from pydantic import BaseModel
from typing import List, Optional


class AuthorBase(BaseModel):
    name: str

    class Config:
        from_attributes = True


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    name: Optional[str] = None


class AuthorSchema(AuthorBase):
    id: int

    class Config:
        from_orm = True
