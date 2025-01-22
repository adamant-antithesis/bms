from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import authors, books
from app.database import AsyncSessionLocal

app = FastAPI(
    title="Book Management System",
    description="API Books Management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request, call_next):
    async with AsyncSessionLocal() as session:
        request.state.db = session
        response = await call_next(request)
    return response

app.include_router(authors.router, prefix="/api/authors", tags=["Authors"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])


# Test Root
@app.get("/")
def read_root():
    return {"message": "Welcome to the Book Management System API!"}
