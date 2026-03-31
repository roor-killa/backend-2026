

from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.drive_service import DriveService
from app.services.document_service import DocumentService
from app.models.user import User

router = APIRouter()
_GOOGLE_CREDENTIALS_BY_USER: dict[int, dict] = {}


def _get_user_credentials(user_id: int, db: Session) -> dict:
    # Placeholder storage until OAuth tokens are persisted in DB.
    creds = _GOOGLE_CREDENTIALS_BY_USER.get(user_id) or _GOOGLE_CREDENTIALS_BY_USER.get(0)
    if not creds:
        raise HTTPException(status_code=400, detail="Google Drive non connecté pour cet utilisateur")
    return creds

@router.get("/connect")
def connect_drive(current_user: User = Depends(get_current_user)):
    """Redirige l'utilisateur vers l'autorisation Google."""
    service = DriveService()
    return {"auth_url": service.get_auth_url()}

@router.get("/oauth/callback")
def oauth_callback(code: str = Query(...), db: Session = Depends(get_db)):
    """Reçoit le code OAuth2 et stocke les tokens."""
    service = DriveService()
    tokens = service.exchange_code(code)
    # TODO : lier les tokens au user via le paramètre `state` OAuth2.
    _GOOGLE_CREDENTIALS_BY_USER[0] = tokens
    return {"message": "Google Drive connecté avec succès"}

@router.get("/files")
def list_drive_files(
    folder_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    credentials = _get_user_credentials(current_user.id, db)
    service = DriveService()
    files = service.list_files(credentials, folder_id)
    return {"files": files, "count": len(files)}

@router.post("/sync/{file_id}")
def sync_drive_file(
    file_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importe et indexe un fichier depuis Drive."""
    credentials = _get_user_credentials(current_user.id, db)
    drive_svc = DriveService()
    doc_svc   = DocumentService(db)

    file_info = drive_svc.get_file_info(file_id, credentials)
    content   = drive_svc.download_file(file_id, file_info["mimeType"], credentials)

    doc = doc_svc.save_from_bytes(
        content=content,
        filename=file_info["name"],
        user=current_user,
        source="drive",
        drive_file_id=file_id,
    )
    background_tasks.add_task(doc_svc.index_document, doc.id)

    return {"message": f"'{file_info['name']}' importé", "document_id": doc.id}
