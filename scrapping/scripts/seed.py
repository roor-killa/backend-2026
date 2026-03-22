from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])


def seed() -> None:
    db = SessionLocal()
    try:
        users = [
            Utilisateur(
                nom="Marie Dubois",
                email="marie@example.com",
                telephone="+596696123456",
                hashed_password=pwd_context.hash("password123"),
            ),
        ]
        db.add_all(users)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
