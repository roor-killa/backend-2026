import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.database import SessionLocal
from app.models.annonce import Annonce
from app.models.utilisateur import Utilisateur
from app.schemas.annonce import CategorieAnnonce
from app.services.auth_service import hash_password


def seed() -> None:
    db = SessionLocal()
    try:
        utilisateur = (
            db.query(Utilisateur)
            .filter(Utilisateur.email == "marie@example.com")
            .first()
        )

        if not utilisateur:
            utilisateur = Utilisateur(
                nom="Marie Dubois",
                email="marie@example.com",
                telephone="+596696123456",
                hashed_password=hash_password("password123"),
                actif=True,
            )
            db.add(utilisateur)
            db.commit()
            db.refresh(utilisateur)
        else:
            utilisateur.nom = "Marie Dubois"
            utilisateur.telephone = "+596696123456"
            utilisateur.hashed_password = hash_password("password123")
            utilisateur.actif = True
            db.commit()
            db.refresh(utilisateur)

        annonces_existantes = (
            db.query(Annonce)
            .filter(
                Annonce.proprietaire_id == utilisateur.id,
                Annonce.titre.in_([
                    "Vente mangues Julie bio",
                    "Cours de yoga face a la mer",
                ]),
            )
            .count()
        )

        if annonces_existantes == 0:
            annonces = [
                Annonce(
                    titre="Vente mangues Julie bio",
                    description="Mangues fraichement recoltees, lot de 5 kg.",
                    prix=3.50,
                    commune="Le Lamentin",
                    categorie=CategorieAnnonce.ALIMENTAIRE,
                    proprietaire_id=utilisateur.id,
                ),
                Annonce(
                    titre="Cours de yoga face a la mer",
                    description="Seance collective de 60 minutes sur la plage.",
                    prix=25.00,
                    commune="Sainte-Anne",
                    categorie=CategorieAnnonce.SERVICES,
                    proprietaire_id=utilisateur.id,
                ),
            ]
            db.add_all(annonces)
            db.commit()

        print("✅ Base de donnees initialisee avec succes !")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
