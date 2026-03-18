from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurResponse
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["Authentification"])

# C'est ce qui indique à FastAPI où les utilisateurs doivent aller pour se connecter
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UtilisateurResponse, status_code=201)
def register(user_data: UtilisateurCreate, db: Session = Depends(get_db)):
    # 1. Vérifier si l'email n'est pas déjà pris
    existant = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    if existant:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    # 2. Créer l'utilisateur avec le mot de passe HACHÉ
    utilisateur = Utilisateur(
        nom=user_data.nom,
        email=user_data.email,
        telephone=user_data.telephone,
        hashed_password=hash_password(user_data.mot_de_passe) # On ne sauvegarde jamais le vrai MDP !
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Chercher l'utilisateur par son email (form_data.username correspond à l'email ici)
    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()

    # 2. Vérifier si l'utilisateur existe ET si le mot de passe est bon
    if not utilisateur or not verify_password(form_data.password, utilisateur.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Si tout est bon, on lui donne son Token JWT 
    token = create_access_token({"sub": utilisateur.email, "id": utilisateur.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "utilisateur": {"id": utilisateur.id, "nom": utilisateur.nom}
    }
# --- LE VIDEUR DE NOTRE API ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 1. On déchiffre le token
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 2. On cherche l'utilisateur dans la base de données
    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == payload.get("sub")).first()
    if not utilisateur:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")
    
    # 3. On laisse passer l'utilisateur !
    return utilisateur