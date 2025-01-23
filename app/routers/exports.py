import json
import csv
from httpx import Response
from io import StringIO
from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.database import get_db
from app.models import Book
from app.schemas.books import BookSchema
from app.utils.rate_limit import rate_limit

router = APIRouter()


@router.get("/export/json")
async def export_books_json(request: Request,db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)

    result = await db.execute(select(Book).options(selectinload(Book.author)))
    books = result.scalars().all()

    books_data = [BookSchema.from_orm(book).dict() for book in books]
    response = Response(content=json.dumps(books_data), media_type="application/json")
    response.headers["Content-Disposition"] = "attachment; filename=books.json"

    return response


@router.get("/export/csv")
async def export_books_csv(request: Request, db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)

    result = await db.execute(select(Book).options(selectinload(Book.author)))
    books = result.scalars().all()

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "title", "author", "genre", "published_year"])
    writer.writeheader()

    for book in books:
        writer.writerow({
            "id": book.id,
            "title": book.title,
            "author": book.author.name,
            "genre": book.genre,
            "published_year": book.published_year
        })

    output.seek(0)

    return Response(content=output.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=books.csv"})
