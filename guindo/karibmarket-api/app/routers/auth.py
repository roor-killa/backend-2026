from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurResponse
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UtilisateurResponse, status_code=201)
def register(user_data: UtilisateurCreate, db: Session = Depends(get_db)):

    existant = db.query(Utilisateur).filter(
        Utilisateur.email == user_data.email
    ).first()

    if existant:
        raise HTTPException(
            status_code=400,
            detail="Email déjà utilisé"
        )

    utilisateur = Utilisateur(
        nom=user_data.nom,
        email=user_data.email,
        telephone=user_data.telephone,
        hashed_password=hash_password(user_data.mot_de_passe)
    )

    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)

    return utilisateur


@router.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):

    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.email == form_data.username
    ).first()

    if not utilisateur:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    if not verify_password(form_data.password, utilisateur.hashed_password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    token = create_access_token({
        "sub": utilisateur.email,
        "id": utilisateur.id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):

    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )

    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.email == payload.get("sub")
    ).first()

    if not utilisateur:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur introuvable"
        )

    return utilisateur