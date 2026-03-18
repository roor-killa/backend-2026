from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Contexte de hachage (on utilise bcrypt, la norme de l'industrie)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(mot_de_passe: str) -> str:
    """Transforme un mot de passe en clair en une chaîne indéchiffrable"""
    return pwd_context.hash(mot_de_passe)

def verify_password(mot_de_passe: str, hashed: str) -> bool:
    """Vérifie si le mot de passe tapé correspond au hash stocké en base"""
    return pwd_context.verify(mot_de_passe, hashed)

def create_access_token(data: dict) -> str:
    """Fabrique un Token JWT signé avec ta clé secrète"""
    payload = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expiration})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    """Déchiffre le token pour vérifier qui est connecté"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None