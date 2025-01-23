import random
from typing import Annotated
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Book, Author
from app.schemas.books import BookSchema
from app.routers.auth import get_current_user
from app.database import get_db
from app.utils.rate_limit import rate_limit


router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=BookSchema)
async def recommend_book_view(request: Request, genre: str = None, author_name: str = None, db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)

    filters = []

    if genre:
        filters.append(Book.genre.ilike(f"%{genre}%"))
    if author_name:
        author_result = await db.execute(
            select(Author.id).filter(Author.name.ilike(f"%{author_name}%"))
        )
        author_ids = author_result.scalars().all()
        if author_ids:
            filters.append(Book.author_id.in_(author_ids))
        else:
            raise HTTPException(status_code=404, detail="No authors found matching the provided name")

    query = select(Book).options(selectinload(Book.author)).filter(*filters)

    result = await db.execute(query)
    books = result.scalars().all()

    if not books:
        genres_result = await db.execute(select(Book.genre).distinct())
        genres = [genre for genre in genres_result.scalars().all()]
        raise HTTPException(
            status_code=404,
            detail=f"No books found. Available genres: {', '.join(genres)}"
        )

    random_book = random.choice(books)

    return random_book
