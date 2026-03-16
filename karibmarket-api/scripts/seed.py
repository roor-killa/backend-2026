import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.models.annonce import Annonce

db = SessionLocal()

# Utilisateur de test
utilisateur = Utilisateur(
    nom="Marie Dupont",
    email="marie@karibmarket.mq",
    telephone="0696000001",
    hashed_password="hashed_secret",
    actif=True,
)
db.add(utilisateur)
db.commit()
db.refresh(utilisateur)
print(f"Utilisateur créé : {utilisateur.nom} (id={utilisateur.id})")

# Annonces de test
annonces = [
    Annonce(
        titre="Mangues bio fraîches",
        prix=3.5,
        commune="Le Lamentin",
        categorie="alimentaire",
        actif=True,
        proprietaire_id=utilisateur.id,
    ),
    Annonce(
        titre="Cours de yoga plage",
        prix=25.0,
        commune="Sainte-Anne",
        categorie="services",
        actif=True,
        proprietaire_id=utilisateur.id,
    ),
]

for a in annonces:
    db.add(a)

db.commit()
print(f"Annonces créées : {len(annonces)}")

db.close()
