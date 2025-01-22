from pydantic import BaseModel, field_validator
from typing import Optional


class AuthorBase(BaseModel):
    name: str

    class Config:
        from_attributes = True


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    name: Optional[str] = None


class AuthorDeleteResponse(BaseModel):
    message: str


class AuthorSchema(AuthorBase):
    id: int

    class Config:
        from_orm = True
