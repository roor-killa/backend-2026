# scripts/seed.py — peupler la base avec des données de test
from app.database import SessionLocal
from app.models.annonce import Annonce
from app.models.utilisateur import Utilisateur
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def seed():
    db = SessionLocal()
    try:
        # Créer des utilisateurs de test
        users = [
            Utilisateur(
                nom="Marie Dubois",
                email="marie@example.com",
                telephone="+596696123456",
                hashed_password=pwd_context.hash("password123")
            ),
        ]
        db.add_all(users)
        db.commit()

        # Créer des annonces de test
        annonces = [
            Annonce(titre="Vente mangues Julie bio", prix=3.50,
                    commune="Le Lamentin", categorie="alimentaire",
                    proprietaire_id=1),
            Annonce(titre="Cours de yoga face à la mer", prix=25.00,
                    commune="Sainte-Anne", categorie="services",
                    proprietaire_id=1),
        ]
        db.add_all(annonces)
        db.commit()
        print("✅ Base de données initialisée avec succès !")
    finally:
        db.close()

if __name__ == "__main__":
    seed()