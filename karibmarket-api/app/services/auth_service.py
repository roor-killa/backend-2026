from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(mot_de_passe: str) -> str:
    """Hacher un mot de passe — JAMAIS stocker en clair"""
    return pwd_context.hash(mot_de_passe)

def verify_password(mot_de_passe: str, hashed: str) -> bool:
    """Vérifier qu'un mot de passe correspond au hash stocké"""
    return pwd_context.verify(mot_de_passe, hashed)

def create_access_token(data: dict) -> str:
    """Créer un JWT signé"""
    payload = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expiration})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    """Décoder et vérifier un JWT"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
