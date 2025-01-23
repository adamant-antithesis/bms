import pytest
import asyncio
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.database import get_db

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
base_url = "http://127.0.0.1:8000/"
LOGIN_URL = "/api/auth/token"


@pytest_asyncio.fixture(scope="module")
def test_engine():
    engine = create_async_engine(DATABASE_URL, echo=True)
    yield engine
    asyncio.run(engine.dispose())


@pytest_asyncio.fixture(name="test_db")
async def test_db_fixture(test_engine):
    SessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture
def client():
    def override_get_db():
        from app.database import AsyncSessionLocal
        with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with AsyncClient(app=app, base_url=base_url) as c:
        yield c
    app.dependency_overrides.clear()


async def login(client):
    login_data = {
        "username": "test_user",
        "password": "test_password"
    }
    response = await client.post(LOGIN_URL, data=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_book_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        endpoint = "api/books/"

        author_response = await client.post("/api/authors/", json={"name": "Test Author"})
        author_id = author_response.json()["id"]

        response = await client.post(endpoint, json={
            "title": "Test Book",
            "genre": "Fiction",
            "published_year": 2024,
            "author_id": author_id
        })
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "Test Book"
        assert data["author_id"] == author_id

        delete_response = await client.delete(f"/api/books/{data['id']}")
        assert delete_response.status_code == 200, delete_response.text

        delete_author_response = await client.delete(f"/api/authors/{author_id}")
        assert delete_author_response.status_code == 200, delete_author_response.text


@pytest.mark.asyncio
async def test_get_books_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        author_response = await client.post("/api/authors/", json={"name": "Author 1"})
        author_id = author_response.json()["id"]

        create_response_1 = await client.post("/api/books/", json={
            "title": "Book 1",
            "genre": "Science",
            "published_year": 2024,
            "author_id": author_id
        })
        create_response_2 = await client.post("/api/books/", json={
            "title": "Book 2",
            "genre": "Fiction",
            "published_year": 2024,
            "author_id": author_id
        })

        response = await client.get("/api/books/")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) >= 2

        delete_response_1 = await client.delete(f"/api/books/{create_response_1.json()['id']}")
        delete_response_2 = await client.delete(f"/api/books/{create_response_2.json()['id']}")
        assert delete_response_1.status_code == 200, delete_response_1.text
        assert delete_response_2.status_code == 200, delete_response_2.text

        delete_author_response = await client.delete(f"/api/authors/{author_id}")
        assert delete_author_response.status_code == 200, delete_author_response.text


@pytest.mark.asyncio
async def test_get_book_by_id_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        author_response = await client.post("/api/authors/", json={"name": "Unique Author"})
        author_id = author_response.json()["id"]

        create_response = await client.post("/api/books/", json={
            "title": "Unique Book",
            "genre": "Science",
            "published_year": 2024,
            "author_id": author_id
        })
        book_id = create_response.json()["id"]

        response = await client.get(f"/api/books/{book_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == book_id
        assert data["title"] == "Unique Book"

        delete_response = await client.delete(f"/api/books/{data['id']}")
        assert delete_response.status_code == 200, delete_response.text

        delete_author_response = await client.delete(f"/api/authors/{author_id}")
        assert delete_author_response.status_code == 200, delete_author_response.text


@pytest.mark.asyncio
async def test_update_book_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        author_response = await client.post("/api/authors/", json={"name": "Old Author"})
        author_id = author_response.json()["id"]

        create_response = await client.post("/api/books/", json={
            "title": "Old Book",
            "genre": "Classic",
            "published_year": 2020,
            "author_id": author_id
        })
        book_id = create_response.json()["id"]

        update_response = await client.put(f"/api/books/{book_id}", json={
            "title": "Updated Book",
            "genre": "Fiction",
            "published_year": 2024,
            "author_id": author_id
        })
        assert update_response.status_code == 200, update_response.text
        data = update_response.json()
        assert data["id"] == book_id
        assert data["title"] == "Updated Book"

        delete_response = await client.delete(f"/api/books/{data['id']}")
        assert delete_response.status_code == 200, delete_response.text

        delete_author_response = await client.delete(f"/api/authors/{author_id}")
        assert delete_author_response.status_code == 200, delete_author_response.text


@pytest.mark.asyncio
async def test_delete_book_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        author_response = await client.post("/api/authors/", json={"name": "To Be Deleted"})
        author_id = author_response.json()["id"]

        create_response = await client.post("/api/books/", json={
            "title": "Book To Be Deleted",
            "genre": "Fiction",
            "published_year": 2024,
            "author_id": author_id
        })
        book_id = create_response.json()["id"]

        delete_response = await client.delete(f"/api/books/{book_id}")
        assert delete_response.status_code == 200, delete_response.text
        data = delete_response.json()
        assert data["message"] == f"Book successfully deleted"

        get_response = await client.get(f"/api/books/{book_id}")
        assert get_response.status_code == 404

        delete_author_response = await client.delete(f"/api/authors/{author_id}")
        assert delete_author_response.status_code == 200, delete_author_response.text
