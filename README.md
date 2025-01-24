# bms
Book Management System

This project is a FastAPI-based application with a PostgreSQL database. 
You can run it either locally or within a Docker container.

- Local Setup

Prerequisites:

Python 3.10 or higher
PostgreSQL database
pip and virtualenv

Steps to Run Locally:

1.Clone the repository:

    git clone https://github.com/adamant-antithesis/bms.git
    cd project-directory

2.Create a virtual environment:

    python -m venv venv

3.Activate the virtual environment:

On macOS/Linux:

    source venv/bin/activate

On Windows:

    .\venv\Scripts\activate

4.Install dependencies:

    pip install -r requirements.txt

5.Set up the database:

Ensure you have PostgreSQL running locally and create a new database for the project.
Create .env file with the following content.
Update the DATABASE_URL in your environment variables or .env file with the correct PostgreSQL URL.

env example: 

    DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/bms_db
    SECRET_KEY=your-secret-key(example: P1xu93OwD2b8mRl5rIxaBfg6ydQy1QFl1rL9YjmNug8=)
    POSTGRES_USER=user(example: postgres)
    POSTGRES_PASSWORD=userpassword(example: postgres)
    POSTGRES_DB=dbname(example: bms_db)

6.Run migrations:

    alembic upgrade head

7.Run the application:

    uvicorn app.main:app --reload

8. Access the API:

    Main path: http://127.0.0.1:8000
    Docs: http://127.0.0.1:8000/docs
    Redoc: http://127.0.0.1:8000/redoc

9. Import some books:

    Place file from directory "import_templates" to this path of csv or json import
   - http://127.0.0.1:8000/api/imports/csv/
   - http://127.0.0.1:8000/api/imports/json/

10. Enjoy! P.S to run tests use - pytest

- Running in Docker

1.Clone the repository:

    git clone https://github.com/adamant-antithesis/bms.git
    cd project-directory

2. Create .env file with the following content:


    DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/bms_db
    DOCKER_DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/bms_db
    SECRET_KEY=your-secret-key(example: P1xu93OwD2b8mRl5rIxaBfg6ydQy1QFl1rL9YjmNug8=)
    POSTGRES_USER=user(example: postgres)
    POSTGRES_PASSWORD=userpassword(example: postgres)
    POSTGRES_DB=dbname(example: bms_db)


3.Build and run the Docker container:

    docker-compose up --build

4.Wait for the database to be ready.

5. Access the API:

    Main path: http://localhost:8000
    Docs: http://localhost:8000/docs
    Redoc: http://localhost:8000/redoc

6. Import some books:

    Place file from directory "import_templates" to this path of csv or json import
   - http://localhost:8000/api/imports/csv/
   - http://localhost:8000/api/imports/json/
    
7. Enjoy! P.S to run tests use - pytest