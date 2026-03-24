# Karib Market API
- python -m venv venv
- venv\Scripts\activate
- pip install fastapi uvicorn[standard]
- uvicorn app.main:app --reload --port 8000
- python -m uvicorn app.main:app --reload --port 8000

# PostgreSQL
- psql postgres
- CREATE USER karib WITH PASSWORD 'karib_pass'
- CREATE DATABASE karibmarket OWNER karib

# Alembic
- alembic init migrations
- alembic revision --autogenerate -m "creation tables initiales"
- alembic upgrade head
- alembic downgrade -1
- alembic history

# Docker
- docker run --name karib-postgres -e POSTGRES_USER=karib -e POSTGRES_PASSWORD=karib_pass -e           POSTGRES_DB=karibmarket -p 5433:5432 -d postgres:15