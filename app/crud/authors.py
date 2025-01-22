from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Author


async def create_author(db: AsyncSession, name: str):
    db_author = Author(name=name)
    db.add(db_author)
    await db.commit()
    await db.refresh(db_author)
    return db_author


async def get_author_by_id(db: AsyncSession, author_id: int):
    result = await db.execute(select(Author).filter(Author.id == author_id))
    return result.scalars().first()


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
    if db_author:
        await db.delete(db_author)
        await db.commit()
    return db_author
