from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import authors, books

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
    from app.database import SessionLocal
    request.state.db = SessionLocal()
    try:
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

app.include_router(authors.router, prefix="/api/authors", tags=["Authors"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])


# Test Root
@app.get("/")
def read_root():
    return {"message": "Welcome to the Book Management System API!"}
