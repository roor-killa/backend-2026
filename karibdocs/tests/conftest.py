import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

# Ensure required settings exist for app.config during imports.
# Uses the PostgreSQL DB exposed by Docker Compose on localhost:5432.
os.environ.setdefault("DATABASE_URL", "postgresql://kd_user:kd_secret@localhost:5432/karibdocs")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

# Ensure `app` package is importable when running tests from repo root.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from app.database import Base, SessionLocal
    from app.main import app as fastapi_app
    from app.services import document_service as document_service_module

    # Import ORM models so metadata contains all required tables.
    import app.models.chat_session  # noqa: F401
    import app.models.document  # noqa: F401
    import app.models.google_drive_credential  # noqa: F401
    import app.models.utilisateur_model  # noqa: F401

    class DummyRAGService:
        def add_documents(self, collection_name, documents, doc_id, force=False):
            return [f"{doc_id}_chunk_{i}" for i, _ in enumerate(documents)]

        def delete_document_chunks(self, collection_name, doc_id):
            return None

    Base.metadata.create_all(bind=SessionLocal.kw["bind"])

    # Keep uploads isolated in temp folder for integration tests.
    monkeypatch.setattr(document_service_module.settings, "UPLOAD_DIR", str(tmp_path / "uploads"))

    # Avoid external vector DB/embedding work while still exercising API routes + SQL DB.
    monkeypatch.setattr(document_service_module, "RAGService", DummyRAGService)
    monkeypatch.setattr(
        document_service_module.DocumentService,
        "index_document",
        lambda self, document_id, force=False: None,
    )

    with TestClient(fastapi_app) as test_client:
        yield test_client


def manual_reset_db_state() -> None:
    """Reset test DB tables only when explicitly called."""
    from app.database import Base, SessionLocal

    table_names = [table.name for table in Base.metadata.sorted_tables]
    db = SessionLocal()
    try:
        if table_names:
            quoted = ", ".join([f'"{name}"' for name in table_names])
            db.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))
            db.commit()
    finally:
        db.close()
