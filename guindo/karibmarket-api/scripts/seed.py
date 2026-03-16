from app.database import SessionLocal
from app.models.annonce import Annonce  # nécessaire pour résoudre la relation SQLAlchemy
from app.models.utilisateur import Utilisateur

db = SessionLocal()

user = Utilisateur(
    nom="Ibrahim",
    email="ibrahim@test.com",
    telephone="+596696000000",
    hashed_password="test"
)

db.add(user)

db.commit()

db.refresh(user)

        # Créer annonces
annonces = [

    Annonce(
            titre="Vente mangues Julie bio",
            description="Mangues fraîches du jardin",
            prix=3.50,
            commune="Le Lamentin",
            categorie="alimentaire",
            proprietaire_id=user.id
        ),

    Annonce(
            titre="Cours de yoga face à la mer",
            description="Séance de yoga au lever du soleil",
            prix=25.00,
            commune="Sainte-Anne",
            categorie="services",
            proprietaire_id=user.id
        )
    ]

db.add_all(annonces)
db.commit()

print("✅ Base de données remplie avec succès")

db.close()