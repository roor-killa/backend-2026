from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate
from app.services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: UtilisateurCreate, db: Session = Depends(get_db)):

    existing = db.query(Utilisateur).filter(Utilisateur.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    new_user = Utilisateur(
        nom=user.nom,
        email=user.email,
        telephone=user.telephone,
        hashed_password=hash_password(user.mot_de_passe)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Utilisateur créé"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
