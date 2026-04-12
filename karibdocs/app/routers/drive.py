

from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import create_access_token, decode_token
from app.services.drive_service import DriveService
from app.services.document_service import DocumentService
from app.models.user import User
from app.models.google_drive_credential import GoogleDriveCredential

router = APIRouter()


def _build_state_token(user_id: int) -> str:
    return create_access_token({"sub": str(user_id), "purpose": "drive_oauth"})


def _get_user_credentials(user_id: int, db: Session) -> dict:
    record = db.query(GoogleDriveCredential).filter(GoogleDriveCredential.user_id == user_id).first()
    if not record:
        raise HTTPException(status_code=400, detail="Google Drive non connecté pour cet utilisateur")
    return record.credentials

@router.get("/connect")
def connect_drive(current_user: User = Depends(get_current_user)):
    """Redirige l'utilisateur vers l'autorisation Google."""
    service = DriveService()
    state = _build_state_token(current_user.id)
    try:
        return {"auth_url": service.get_auth_url(state=state), "state": state}
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/oauth/callback")
def oauth_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Reçoit le code OAuth2 et stocke les tokens."""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth Google refusé: {error}")

    if not state:
        raise HTTPException(status_code=400, detail="Paramètre OAuth state manquant")

    if not code:
        raise HTTPException(status_code=400, detail="Paramètre OAuth code manquant")

    payload = decode_token(state)
    if not payload or payload.get("purpose") != "drive_oauth":
        raise HTTPException(status_code=400, detail="État OAuth invalide")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Utilisateur OAuth introuvable")

    service = DriveService()
    try:
        tokens = service.exchange_code(code)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Échec échange du code OAuth: {exc}") from exc
    record = db.query(GoogleDriveCredential).filter(GoogleDriveCredential.user_id == int(user_id)).first()
    if record:
        record.credentials = tokens
    else:
        record = GoogleDriveCredential(user_id=int(user_id), credentials=tokens)
        db.add(record)
    db.commit()
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
        mime_type=file_info.get("mimeType"),
    )
    background_tasks.add_task(doc_svc.index_document, doc.id)

    return {"message": f"'{file_info['name']}' importé", "document_id": doc.id}
