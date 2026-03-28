
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from app.config import settings

def hash_password(mot_de_passe: str) -> str:
    """Hacher un mot de passe — JAMAIS stocker en clair"""
    hashed = bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(mot_de_passe: str, hashed: str) -> bool:
    """Vérifier qu'un mot de passe correspond au hash stocké"""
    try:
        return bcrypt.checkpw(mot_de_passe.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False

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