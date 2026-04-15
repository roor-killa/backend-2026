import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Base de données SQLite en mémoire pour les tests
TEST_DATABASE_URL = "sqlite:///./test_battleship.db"

engine_test = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(autouse=True)
def reset_tables():
    """Vide toutes les tables entre chaque test."""
    yield
    db = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()
"""
Configuration Pytest — Fixtures partagées entre tous les tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# ── Base de données de test (SQLite en mémoire) ───────
# Complètement isolée de la BDD de développement
TEST_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


def override_get_db():
    """Remplace get_db() par une session de test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Fixtures ──────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crée les tables avant tous les tests, les supprime après."""
    import app.models  # noqa: F401 — enregistre les modèles
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(autouse=True)
def clean_tables():
    """Vide toutes les tables avant chaque test pour l'isolation."""
    yield
    db = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    """Client HTTP de test FastAPI avec la BDD de test injectée."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    """Session BDD de test directe (pour les tests de services)."""
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


# ── Helpers de création rapide ─────────────────────────

@pytest.fixture
def player_ibrahim(client):
    """Crée le joueur Ibrahim et retourne sa réponse JSON."""
    res = client.post("/players/", json={"pseudo": "Ibrahim"})
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def player_mohand(client):
    """Crée le joueur Mohand et retourne sa réponse JSON."""
    res = client.post("/players/", json={"pseudo": "Mohand"})
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def solo_game(client, player_ibrahim):
    """Crée une partie solo (facile) pour Ibrahim."""
    res = client.post(
        "/games/",
        params={"player_id": player_ibrahim["id"]},
        json={"mode": "solo", "difficulty": "easy"},
    )
    assert res.status_code == 201
    return res.json()


SAMPLE_SHIPS = [
    {"type": "carrier",    "row": 0, "col": 0, "orientation": "horizontal"},
    {"type": "cruiser",    "row": 1, "col": 0, "orientation": "horizontal"},
    {"type": "destroyer",  "row": 2, "col": 0, "orientation": "horizontal"},
    {"type": "submarine",  "row": 3, "col": 0, "orientation": "horizontal"},
    {"type": "torpedo",    "row": 4, "col": 0, "orientation": "horizontal"},
]