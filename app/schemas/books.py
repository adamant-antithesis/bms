from pydantic import BaseModel, conint
from enum import Enum
from typing import Optional

from app.schemas.authors import AuthorSchema


class GenreEnum(str, Enum):
    fiction = "Fiction"
    non_fiction = "Non-Fiction"
    adventure = "Adventure"
    science = "Science"
    history = "History"
    biography = "Biography"
    fantasy = "Fantasy"
    mystery = "Mystery"
    dystopian = "Dystopian"
    romance = "Romance"
    satire = "Satire"
    political_satire = "Political Satire"
    classic = "Classic"


class BookBase(BaseModel):
    title: str
    genre: GenreEnum
    published_year: conint(ge=1800, le=2025)
    author_id: int

    class Config:
        from_attributes = True


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    title: Optional[str] = None
    genre: Optional[GenreEnum] = None
    published_year: Optional[conint(ge=1800, le=2025)] = None
    author_id: Optional[int] = None


class BookDeleteResponse(BaseModel):
    message: str


class BookSchema(BookBase):
    id: int
    author: AuthorSchema

    class Config:
        from_orm = True


class BookFilterParams(BaseModel):
    title: Optional[str] = None
    author_name: Optional[str] = None
    genre: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
