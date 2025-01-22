from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import Book, Author
from app.schemas.books import BookSchema, BookDeleteResponse


async def create_book(db: AsyncSession, title: str, genre: str, published_year: int, author_id: int):
    result = await db.execute(select(Author).filter(Author.id == author_id))
    existing_author = result.scalars().first()

    if not existing_author:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} does not exist.")

    db_book = Book(title=title, genre=genre, published_year=published_year, author_id=author_id)
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)

    result = await db.execute(select(Book).filter(Book.id == db_book.id).options(selectinload(Book.author)))
    db_book_with_author = result.scalars().first()

    return BookSchema.from_orm(db_book_with_author)


async def get_book_by_id(db: AsyncSession, book_id: int):

    result = await db.execute(
        select(Book).filter(Book.id == book_id).options(selectinload(Book.author))
    )
    book = result.scalars().first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return BookSchema.from_orm(book)


async def get_books_list(db: AsyncSession, skip: int = 0, limit: int = 10):

    result = await db.execute(
        select(Book)
        .options(selectinload(Book.author))
        .offset(skip)
        .limit(limit)
    )

    books = result.scalars().all()

    return [BookSchema.from_orm(book) for book in books]


async def update_book_by_id(db: AsyncSession, book_id: int, title: str, genre: str, published_year: int,
                            author_id: int):

    result = await db.execute(select(Book).filter(Book.id == book_id).options(selectinload(Book.author)))
    db_book = result.scalars().first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if title:
        db_book.title = title
    if genre:
        db_book.genre = genre
    if published_year:
        db_book.published_year = published_year
    if author_id:
        db_book.author_id = author_id

    await db.commit()
    await db.refresh(db_book)

    result = await db.execute(select(Book).filter(Book.id == db_book.id).options(selectinload(Book.author)))
    updated_book = result.scalars().first()

    return BookSchema.from_orm(updated_book)


async def delete_book_by_id(db: AsyncSession, book_id: int):

    result = await db.execute(select(Book).filter(Book.id == book_id).options(selectinload(Book.author)))
    db_book = result.scalars().first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.delete(db_book)
    await db.commit()

    return BookDeleteResponse(message="Book successfully deleted")
