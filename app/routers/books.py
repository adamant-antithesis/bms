from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.books import BookSchema, BookCreate, BookUpdate
from app.crud.books import (create_book,
                            get_book_by_id,
                            get_books_list,
                            update_book_by_id,
                            delete_book_by_id)
from app.database import get_db

router = APIRouter()


@router.post("/books/", response_model=BookSchema)
async def create_book_view(book: BookCreate, db: AsyncSession = Depends(get_db)):
    return await create_book(db=db, title=book.title, genre=book.genre,
                             published_year=book.published_year, author_id=book.author_id)


@router.get("/books/", response_model=list[BookSchema])
async def get_books_view(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_books_list(db=db, skip=skip, limit=limit)


@router.get("/books/{book_id}", response_model=BookSchema)
async def get_book_view(book_id: int, db: AsyncSession = Depends(get_db)):
    return await get_book_by_id(db=db, book_id=book_id)


@router.put("/books/{book_id}", response_model=BookSchema)
async def update_book_view(book_id: int, book: BookUpdate, db: AsyncSession = Depends(get_db)):
    return await update_book_by_id(db=db, book_id=book_id, title=book.title, genre=book.genre,
                                   published_year=book.published_year, author_id=book.author_id)


@router.delete("/books/{book_id}", response_model=BookSchema)
async def delete_book_view(book_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_book_by_id(db=db, book_id=book_id)
