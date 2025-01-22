from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Author, Book
from app.schemas.authors import AuthorSchema


async def create_author(db: AsyncSession, name: str):

    existing_author = await db.execute(select(Author).filter(Author.name == name))
    existing_author = existing_author.scalars().first()

    if existing_author:
        raise HTTPException(status_code=400, detail=f"Author with name '{name}' already exists.")

    if not name.strip():
        raise HTTPException(status_code=400, detail="Name is required and can't be empty.")

    try:
        db_author = Author(name=name)
        db.add(db_author)
        await db.commit()
        await db.refresh(db_author)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return AuthorSchema.from_orm(db_author)


async def get_author_by_id(db: AsyncSession, author_id: int):
    result = await db.execute(select(Author).filter(Author.id == author_id))
    author = result.scalars().first()

    if author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")

    return author


async def get_authors_list(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Author).offset(skip).limit(limit))
    return result.scalars().all()


async def update_author_by_id(db: AsyncSession, author_id: int, name: str):
    db_author = await get_author_by_id(db, author_id)
    if db_author:
        db_author.name = name
        await db.commit()
        await db.refresh(db_author)
    return db_author


async def delete_author_by_id(db: AsyncSession, author_id: int):
    db_author = await get_author_by_id(db, author_id)

    if db_author is None:
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")

    result = await db.execute(select(Book).filter(Book.author_id == author_id))
    books = result.scalars().all()

    if books:
        raise HTTPException(status_code=400,
                            detail=f"Author with id {author_id} has books and can't be deleted, delete books first")

    await db.delete(db_author)
    await db.commit()

    return {"message": f"Author with id {author_id} successfully deleted"}
