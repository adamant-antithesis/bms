from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware
from app.routers import authors, books, imports, auth, exports, recommend
from app.database import AsyncSessionLocal
from app.models import User
from passlib.context import CryptContext
from sqlalchemy.future import select

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_test_user():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "test_user"))
        user = result.scalars().first()

        if not user:
            hashed_password = bcrypt_context.hash("test_password")
            new_user = User(username="test_user", hashed_password=hashed_password)
            db.add(new_user)
            await db.commit()
            print("Test user created successfully")


app = FastAPI(
    title="Book Management System",
    description="API Books Management",
    version="1.0.0",
    on_startup=[create_test_user]
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
app.include_router(recommend.router, prefix="/api/recommend", tags=["Recommend"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])
app.include_router(imports.router, prefix="/api/imports", tags=["Import"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(exports.router, prefix="/api/exports", tags=["exports"])


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
