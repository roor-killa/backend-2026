"""
conftest.py — configuration globale des tests KaribMarket
Gère la création/destruction de la base SQLite de test.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient

# --------------------------------------------------
# Configuration base de test SQLite
# --------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
DB_PATH = "./test.db"

# Suppression préalable pour repartir d'un état propre
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Initialiser le cache en mémoire (pas de Redis en test)
FastAPICache.init(InMemoryBackend(), prefix="test-cache")

# Client partagé par tous les modules de test
client = TestClient(app)
