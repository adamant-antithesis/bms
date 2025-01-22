from pydantic import BaseModel
from typing import List, Optional


class AuthorBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    name: Optional[str] = None


class Author(AuthorBase):
    id: int
    books: List[str] = []

    class Config:
        orm_mode = True
