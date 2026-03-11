"""
Peupler la base de données avec des données de test.
Usage : python scripts/seed.py
"""
import sys
import os

# Ajouter la racine du projet au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.annonce import Annonce
from app.models.utilisateur import Utilisateur
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed():
    db = SessionLocal()
    try:
        # Éviter les doublons si le script est relancé
        if db.query(Utilisateur).count() > 0:
            print("La base contient déjà des données. Seed ignoré.")
            return

        # Créer des utilisateurs de test
        users = [
            Utilisateur(
                nom="Marie Dubois",
                email="marie@example.com",
                telephone="+596696123456",
                hashed_password=pwd_context.hash("password123")
            ),
            Utilisateur(
                nom="Jean-Pierre Martin",
                email="jp@example.com",
                telephone="+596696654321",
                hashed_password=pwd_context.hash("password123")
            ),
        ]
        db.add_all(users)
        db.commit()
        db.refresh(users[0])
        db.refresh(users[1])

        # Créer des annonces de test
        annonces = [
            Annonce(
                titre="Vente mangues Julie bio",
                prix=3.50,
                commune="Le Lamentin",
                categorie="alimentaire",
                proprietaire_id=users[0].id
            ),
            Annonce(
                titre="Cours de yoga face à la mer",
                prix=25.00,
                commune="Sainte-Anne",
                categorie="services",
                proprietaire_id=users[0].id
            ),
            Annonce(
                titre="Location VTT tout terrain",
                prix=15.00,
                commune="Le Morne-Rouge",
                categorie="loisirs",
                proprietaire_id=users[1].id
            ),
        ]
        db.add_all(annonces)
        db.commit()
        print("Base de données initialisée avec succès !")
        print(f"  - {len(users)} utilisateurs créés")
        print(f"  - {len(annonces)} annonces créées")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
