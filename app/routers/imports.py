import csv
import json
from io import StringIO
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Author, Book
from app.utils.rate_limit import rate_limit

router = APIRouter()


@router.post("/csv/")
async def import_books_and_authors_csv(request: Request, file: UploadFile = File(...),
                                       db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)
    try:
        contents = await file.read()
        csv_file = StringIO(contents.decode("utf-8"))
        reader = csv.DictReader(csv_file)

        author_id_map = {}
        imported_authors_count, imported_books_count, skipped_books_count = 0, 0, 0

        async def get_or_create_author(author_name):
            if author_name not in author_id_map:
                existing_author = await db.execute(select(Author).filter(Author.name == author_name))
                existing_author = existing_author.scalars().first()

                if not existing_author:
                    new_author = Author(name=author_name)
                    db.add(new_author)
                    await db.commit()
                    await db.refresh(new_author)
                    author_id_map[author_name] = new_author.id
                    return new_author.id, True
                else:
                    author_id_map[author_name] = existing_author.id
            return author_id_map[author_name], False

        for row in reader:
            _, created = await get_or_create_author(row["author_name"])
            if created:
                imported_authors_count += 1

        csv_file.seek(0)
        next(reader)

        for row in reader:
            author_id, _ = await get_or_create_author(row["author_name"])
            existing_book = await db.execute(
                select(Book).filter(
                    Book.title == row["title"],
                    Book.author_id == author_id,
                )
            )
            if existing_book.scalars().first():
                skipped_books_count += 1
                continue

            db.add(Book(
                title=row["title"],
                genre=row["genre"],
                published_year=int(row["published_year"]),
                author_id=author_id,
            ))
            imported_books_count += 1

        await db.commit()

        if imported_authors_count == 0 and imported_books_count == 0:
            return {"message": "No authors or books were imported."}

        return {
            "message": "Import completed successfully.",
            "imported_authors": imported_authors_count,
            "imported_books": imported_books_count,
            "skipped_books": skipped_books_count,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process the file, check the format and try again.")


@router.post("/json/")
async def import_books_and_authors_json(request: Request, file: UploadFile, db: AsyncSession = Depends(get_db)):
    user_ip = request.client.host
    rate_limit(user_ip=user_ip)
    try:
        contents = await file.read()
        data = json.loads(contents)

        if "authors" not in data or not isinstance(data["authors"], list):
            raise HTTPException(status_code=400, detail="Invalid JSON format. 'authors' field is required.")

        imported_authors_count, imported_books_count, skipped_books_count = 0, 0, 0

        for author_data in data["authors"]:
            author_name = author_data.get("name")
            if not author_name:
                continue

            existing_author = await db.execute(select(Author).filter(Author.name == author_name))
            existing_author = existing_author.scalars().first()

            if not existing_author:
                db_author = Author(name=author_name)
                db.add(db_author)
                await db.commit()
                await db.refresh(db_author)
                new_author_id = db_author.id
                imported_authors_count += 1
            else:
                new_author_id = existing_author.id

            for book_data in author_data.get("books", []):
                title = book_data.get("title")
                if not title:
                    continue

                existing_book = await db.execute(
                    select(Book).filter(Book.title == title, Book.author_id == new_author_id)
                )
                if existing_book.scalars().first():
                    skipped_books_count += 1
                    continue

                db_book = Book(
                    title=title,
                    genre=book_data.get("genre", ""),
                    published_year=book_data.get("published_year", 0),
                    author_id=new_author_id,
                )
                db.add(db_book)
                imported_books_count += 1

        await db.commit()

        if imported_authors_count == 0 and imported_books_count == 0:
            return {"message": "No authors or books were imported."}

        return {
            "message": "Import completed successfully.",
            "imported_authors": imported_authors_count,
            "imported_books": imported_books_count,
            "skipped_books": skipped_books_count,
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process the file, check the format and try again.")
