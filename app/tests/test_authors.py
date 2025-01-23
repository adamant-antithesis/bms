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
async def test_create_author_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        endpoint = "api/authors/"
        response = await client.post(endpoint, json={"name": "Test Author"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == "Test Author"
        delete_response = await client.delete(f"/api/authors/{data['id']}")
        assert delete_response.status_code == 200, delete_response.text


@pytest.mark.asyncio
async def test_get_authors_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        create_response_1 = await client.post("/api/authors/", json={"name": "Author 1"})
        create_response_2 = await client.post("/api/authors/", json={"name": "Author 2"})

        response = await client.get("/api/authors/")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) >= 2

        delete_response_1 = await client.delete(f"/api/authors/{create_response_1.json()['id']}")
        delete_response_2 = await client.delete(f"/api/authors/{create_response_2.json()['id']}")
        assert delete_response_1.status_code == 200, delete_response_1.text
        assert delete_response_2.status_code == 200, delete_response_2.text


@pytest.mark.asyncio
async def test_get_author_by_id_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        create_response = await client.post("/api/authors/", json={"name": "Unique Author"})
        author_id = create_response.json()["id"]

        response = await client.get(f"/api/authors/{author_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == author_id
        assert data["name"] == "Unique Author"

        delete_response = await client.delete(f"/api/authors/{data['id']}")
        assert delete_response.status_code == 200, delete_response.text


@pytest.mark.asyncio
async def test_update_author_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        create_response = await client.post("/api/authors/", json={"name": "Old Name"})
        author_id = create_response.json()["id"]

        update_response = await client.put(f"/api/authors/{author_id}", json={"name": "New Name"})
        assert update_response.status_code == 200, update_response.text
        data = update_response.json()
        assert data["id"] == author_id
        assert data["name"] == "New Name"

        delete_response = await client.delete(f"/api/authors/{data['id']}")
        assert delete_response.status_code == 200, delete_response.text


@pytest.mark.asyncio
async def test_delete_author_route(test_db):
    async with AsyncClient(base_url=base_url) as client:
        access_token = await login(client)
        client.headers["Authorization"] = f"Bearer {access_token}"

        create_response = await client.post("/api/authors/", json={"name": "To Be Deleted"})
        author_id = create_response.json()["id"]

        delete_response = await client.delete(f"/api/authors/{author_id}")
        assert delete_response.status_code == 200, delete_response.text
        data = delete_response.json()
        assert data["message"] == f"Author with id: {author_id} successfully deleted"

        get_response = await client.get(f"/api/authors/{author_id}")
        assert get_response.status_code == 404
