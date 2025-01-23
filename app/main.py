from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

from app.routers import authors, books, imports
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
app.include_router(imports.router, prefix="/api/imports", tags=["Import"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    error_message = exc.errors()[0].get("msg", "Invalid input.")
    return JSONResponse(status_code=422, content={"detail": error_message})


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request, exc: ValidationError):
    error_message = exc.errors()[0].get("msg", "Invalid input.")
    return JSONResponse(status_code=422, content={"detail": error_message})


# Test Root
@app.get("/")
def read_root():
    return {"message": "Welcome to the Book Management System API!"}
