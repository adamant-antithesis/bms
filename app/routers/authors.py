from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.authors import (AuthorSchema,
                                 AuthorCreate,
                                 AuthorDeleteResponse)
from app.crud.authors import (create_author,
                              get_author_by_id,
                              get_authors_list,
                              update_author_by_id,
                              delete_author_by_id)
from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=AuthorSchema)
async def create_author_route(user: user_dependency, author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    return await create_author(db=db, name=author.name)


@router.get("/", response_model=list[AuthorSchema])
async def get_authors(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    authors = await get_authors_list(db=db, skip=skip, limit=limit)
    return authors


@router.get("/{author_id}", response_model=AuthorSchema)
async def get_author_route(author_id: int, db: AsyncSession = Depends(get_db)):
    author = await get_author_by_id(db=db, author_id=author_id)
    return author


@router.put("/{author_id}", response_model=AuthorSchema)
async def update_author_route(user: user_dependency, author_id: int, author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    return await update_author_by_id(db=db, author_id=author_id, name=author.name)


@router.delete("/{author_id}", response_model=AuthorDeleteResponse)
async def delete_author_route(user: user_dependency, author_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_author_by_id(db=db, author_id=author_id)
