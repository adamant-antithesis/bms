from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Book


async def create_book(db: AsyncSession, title: str, genre: str, published_year: int, author_id: int):
    db_book = Book(title=title, genre=genre, published_year=published_year, author_id=author_id)
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book


async def get_book_by_id(db: AsyncSession, book_id: int):
    result = await db.execute(select(Book).filter(Book.id == book_id))
    return result.scalars().first()


async def get_books_list(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Book).offset(skip).limit(limit))
    return result.scalars().all()


async def update_book_by_id(db: AsyncSession, book_id: int, title: str, genre: str, published_year: int,
                            author_id: int):
    db_book = await get_book_by_id(db, book_id)
    db_book = await get_book_by_id(db, book_id)
    if db_book:
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
    return db_book


async def delete_book_by_id(db: AsyncSession, book_id: int):
    db_book = await get_book_by_id(db, book_id)
    if db_book:
        await db.delete(db_book)
        await db.commit()
    return db_book
