from typing import Annotated
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.auth import get_current_user
from app.schemas.books import (BookSchema,
                               BookCreate,
                               BookUpdate,
                               BookDeleteResponse,
                               BookFilterParams)
from app.crud.books import (create_book,
                            get_book_by_id,
                            get_books_list,
                            update_book_by_id,
                            delete_book_by_id)
from app.database import get_db
from app.utils.rate_limit import rate_limit

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/", response_model=BookSchema)
async def create_book_view(user: user_dependency, book: BookCreate, request: Request, db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)
    return await create_book(db=db, title=book.title, genre=book.genre,
                             published_year=book.published_year, author_id=book.author_id)


@router.get("/", response_model=list[BookSchema])
async def get_books_view(
        request: Request,
        skip: int = 0,
        limit: int = 10,
        filter_params: BookFilterParams = Depends(),
        db: AsyncSession = Depends(get_db),
):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)
    return await get_books_list(
        db=db,
        skip=skip,
        limit=limit,
        title=filter_params.title,
        author_name=filter_params.author_name,
        genre=filter_params.genre,
        year_from=filter_params.year_from,
        year_to=filter_params.year_to,
        sort_by=filter_params.sort_by,
        sort_order=filter_params.sort_order,
    )


@router.get("/{book_id}", response_model=BookSchema)
async def get_book_view(book_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)
    return await get_book_by_id(db=db, book_id=book_id)


@router.put("/{book_id}", response_model=BookSchema)
async def update_book_view(user: user_dependency, book_id: int, book: BookUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)
    return await update_book_by_id(db=db, book_id=book_id, title=book.title, genre=book.genre,
                                   published_year=book.published_year, author_id=book.author_id)


@router.delete("/{book_id}", response_model=BookDeleteResponse)
async def delete_book_view(user: user_dependency, book_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)
    return await delete_book_by_id(db=db, book_id=book_id)
