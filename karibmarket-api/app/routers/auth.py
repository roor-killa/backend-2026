from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token
)

from app.schemas.utilisateur import UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])

users_db = []

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# REGISTER
@router.post("/register")
def register(user: UserCreate):

    # Vérifie email unique
    for u in users_db:
        if u["email"] == user.email:
            raise HTTPException(400, "Email déjà utilisé")

    new_user = {
        "id": len(users_db) + 1,
        "nom": user.nom,
        "email": user.email,
        "telephone": user.telephone,
        "password": hash_password(user.mot_de_passe)  # ⚠️ hash
    }

    users_db.append(new_user)

    return {"message": "Utilisateur créé"}

# LOGIN (reste pareil ⚠️)
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    for user in users_db:
        if user["email"] == form_data.username:
            if verify_password(form_data.password, user["password"]):

                token = create_access_token({
                    "id": user["id"],
                    "sub": user["email"]
                })

                return {
                    "access_token": token,
                    "token_type": "bearer"
                }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants incorrects"
    )

# GET CURRENT USER
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)

    if not payload:
        raise HTTPException(401, "Token invalide")

    return payload