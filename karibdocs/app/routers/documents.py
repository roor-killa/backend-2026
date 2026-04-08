

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.document_service import DocumentService
from app.models.user import User
from app.schemas.document import DocumentOut, DocumentListOut

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}

ALLOWED_EXTENSIONS = set(ALLOWED_TYPES.values())


def _normalize_mime(content_type: str | None) -> str:
    return (content_type or "").split(";", 1)[0].strip().lower()


def _guess_type_from_head(head: bytes) -> str | None:
    if head.startswith(b"%PDF-"):
        return "pdf"
    if head.startswith(b"PK"):
        # Les .docx sont des archives zip (signature PK)
        return "docx"
    if b"\x00" not in head:
        try:
            head.decode("utf-8")
            return "txt"
        except UnicodeDecodeError:
            return None
    return None


async def _is_supported_upload(file: UploadFile) -> bool:
    """Accepte MIME connu, fallback extension et signature pour octet-stream."""
    content_type = _normalize_mime(file.content_type)

    if content_type in ALLOWED_TYPES:
        return True

    filename = (file.filename or "").lower()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""

    if content_type == "application/octet-stream" and ext in ALLOWED_EXTENSIONS:
        return True

    if content_type == "application/octet-stream":
        head = await file.read(4096)
        await file.seek(0)
        guessed_ext = _guess_type_from_head(head)
        return guessed_ext in ALLOWED_EXTENSIONS

    return False

@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload un document et l'indexe en arrière-plan."""
    if not await _is_supported_upload(file):
        raise HTTPException(status_code=400, detail=f"Type non supporté: {file.content_type}")

    service = DocumentService(db)
    document = await service.save_document(file, current_user)

    # Indexation asynchrone (ne bloque pas la réponse HTTP)
    background_tasks.add_task(service.index_document, document.id)

    return document

@router.get("/", response_model=DocumentListOut)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    documents = service.get_user_documents(current_user.id)
    return {
        "count": len(documents),
        "documents": documents,
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    try:
        service.delete_document(document_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "Document supprimé avec succès"}

@router.post("/{document_id}/reindex")
def reindex_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    background_tasks.add_task(service.index_document, document_id, force=True)
    return {"message": "Ré-indexation lancée en arrière-plan"}