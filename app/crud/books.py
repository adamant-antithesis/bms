from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, asc, desc
from typing import Optional
from app.models import Book, Author
from app.schemas.books import BookSchema, BookDeleteResponse


async def create_book(db: AsyncSession, title: str, genre: str, published_year: int, author_id: int):

    result = await db.execute(select(Book).filter(Book.title == title))
    existing_book = result.scalars().first()

    if existing_book:
        raise HTTPException(status_code=400, detail=f"Book with title '{title}' already exists.")

    result = await db.execute(select(Author).filter(Author.id == author_id))
    existing_author = result.scalars().first()

    if not existing_author:
        raise HTTPException(status_code=404, detail=f"Author with id: {author_id} does not exist.")

    try:
        db_book = Book(title=title, genre=genre, published_year=published_year, author_id=author_id)
        db.add(db_book)
        await db.commit()
        await db.refresh(db_book)

        result = await db.execute(select(Book).filter(Book.id == db_book.id).options(selectinload(Book.author)))
        db_book_with_author = result.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request")

    return BookSchema.from_orm(db_book_with_author)


async def get_book_by_id(db: AsyncSession, book_id: int):

    try:
        result = await db.execute(
            select(Book).filter(Book.id == book_id).options(selectinload(Book.author))
        )
        book = result.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request")

    if not book:
        raise HTTPException(status_code=404, detail=f"Book with id: {book_id} not found")

    return BookSchema.from_orm(book)


async def get_books_list(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    title: Optional[str] = None,
    author_name: Optional[str] = None,
    genre: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
):
    filters = []

    if title:
        filters.append(Book.title.ilike(f"%{title}%"))
    if genre:
        filters.append(Book.genre.ilike(f"%{genre}%"))
    if year_from is not None:
        filters.append(Book.published_year >= year_from)
    if year_to is not None:
        filters.append(Book.published_year <= year_to)

    if author_name:
        author_result = await db.execute(select(Author.id).filter(Author.name.ilike(f"%{author_name}%")))
        author_ids = author_result.scalars().all()
        if author_ids:
            filters.append(Book.author_id.in_(author_ids))
        else:
            return []

    query = (
        select(Book)
        .options(selectinload(Book.author))
        .where(and_(*filters) if filters else True)
        .offset(skip)
        .limit(limit)
    )

    if sort_by:
        if sort_by == "author_name":
            query = query.join(Author).order_by(
                asc(Author.name) if sort_order == "asc" else desc(Author.name)
            )
        elif hasattr(Book, sort_by):
            sort_field = getattr(Book, sort_by)
            query = query.order_by(
                asc(sort_field) if sort_order == "asc" else desc(sort_field)
            )

    try:
        result = await db.execute(query)
        books = result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request")

    return [BookSchema.from_orm(book) for book in books]


async def update_book_by_id(db: AsyncSession, book_id: int, title: str, genre: str, published_year: int,
                            author_id: int):

    try:
        result = await db.execute(select(Book).filter(Book.id == book_id).options(selectinload(Book.author)))
        db_book = result.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request")

    if not db_book:
        raise HTTPException(status_code=404, detail=f"Book with id: {book_id} not found")

    result = await db.execute(select(Author).filter(Author.id == author_id))
    existing_author = result.scalars().first()

    if not existing_author:
        raise HTTPException(status_code=404, detail=f"Author with id: {author_id} does not exist.")

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
    try:
        result = await db.execute(select(Book).filter(Book.id == book_id).options(selectinload(Book.author)))
        db_book = result.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request")

    if not db_book:
        raise HTTPException(status_code=404, detail=f"Book with id: {book_id} not found")

    await db.delete(db_book)
    await db.commit()

    return BookDeleteResponse(message="Book successfully deleted")
