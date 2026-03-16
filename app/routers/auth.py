from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.exc import UnknownHashError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurResponse
from app.services.auth_service import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentification"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UtilisateurResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UtilisateurCreate, db: Session = Depends(get_db)) -> Utilisateur:
    existant = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    if existant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email est deja utilise")

    utilisateur = Utilisateur(
        nom=user_data.nom,
        email=user_data.email,
        telephone=user_data.telephone,
        hashed_password=hash_password(user_data.mot_de_passe),
        actif=True,
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()

    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_ok = False
    try:
        password_ok = verify_password(form_data.password, utilisateur.hashed_password)
    except UnknownHashError:
        password_ok = form_data.password == utilisateur.hashed_password
        if password_ok:
            utilisateur.hashed_password = hash_password(form_data.password)
            db.commit()

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": utilisateur.email, "id": utilisateur.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "utilisateur": {"id": utilisateur.id, "nom": utilisateur.nom},
    }


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expire",
            headers={"WWW-Authenticate": "Bearer"},
        )

    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == payload.get("sub")).first()

    if not utilisateur or not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return utilisateur
