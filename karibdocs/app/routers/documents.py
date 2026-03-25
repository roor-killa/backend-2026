
# app/routers/documents.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.document_service import DocumentService
from app.models.user import User
from app.schemas.document import DocumentOut

# / Permet de creer les differents routes /
router = APIRouter()


ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}

# / tache asynchrone et background qui sauvegarde un document uploader par un utilisateur /
@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload un document et l'indexe en arrière-plan."""
    if file.content_type not in ALLOWED_TYPES: # / Verifie si le format est bon /
        raise HTTPException(status_code=400, detail=f"Type non supporté: {file.content_type}")

    service = DocumentService(db)
    document = await service.save_document(file, current_user)

    # Indexation asynchrone (ne bloque pas la réponse HTTP)
    background_tasks.add_task(service.index_document, document.id)

    return document

# / Recupere tous les documents uploader par l'utilisateur /
@router.get("/", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    return service.get_user_documents(current_user.id)


# / Permet a l'utilisateur de supprimer un de ces documents /
@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    service.delete_document(document_id, current_user.id)
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