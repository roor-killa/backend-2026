from fastapi import APIRouter, HTTPException
from app.models.annonce import Annonce
router = APIRouter()

# Base de données temporaire
annonces = [
    {
        "id": 1,
        "titre": "Mangues Julie bio",
        "description": "Mangues fraîchement récoltées",
        "prix": 3.5,
        "commune": "Le Lamentin",
        "categorie": "alimentaire"
    },
    {
        "id": 2,
        "titre": "Cours de guitare",
        "description": "Cours pour débutants",
        "prix": 20,
        "commune": "Fort-de-France",
        "categorie": "services"
    },
    {
        "id": 3,
        "titre": "Location scooter",
        "description": "Scooter 125cc en bon état",
        "prix": 35,
        "commune": "Sainte-Anne",
        "categorie": "vehicules"
    },
    {
        "id": 4,
        "titre": "Appartement T2",
        "description": "Appartement proche plage",
        "prix": 750,
        "commune": "Trois-Ilets",
        "categorie": "immobilier"
    },
    {
        "id": 5,
        "titre": "Cours de yoga",
        "description": "Yoga face à la mer",
        "prix": 15,
        "commune": "Sainte-Luce",
        "categorie": "loisirs"
    }
]

# Liste des annonces
@router.get("/annonces")
def get_annonces(commune: str = None, categorie: str = None):

    resultat = annonces

    if commune:
        resultat = [a for a in resultat if a["commune"] == commune]

    if categorie:
        resultat = [a for a in resultat if a["categorie"] == categorie]

    return resultat


# Détail d'une annonce
@router.get("/annonces/{id}")
def get_annonce(id: int):

    for annonce in annonces:
        if annonce["id"] == id:
            return annonce

    raise HTTPException(status_code=404, detail="Annonce introuvable")


# Créer une annonce
@router.post("/annonces")
def create_annonce(annonce: Annonce):

    nouvelle_annonce = annonce.model_dump()
    nouvelle_annonce["id"] = len(annonces) + 1

    annonces.append(nouvelle_annonce)

    return nouvelle_annonce

# Supprimer une annonce
@router.delete("/annonces/{id}")
def delete_annonce(id: int):

    for annonce in annonces:
        if annonce["id"] == id:
            annonces.remove(annonce)
            return {"message": "Annonce supprimée"}

    raise HTTPException(status_code=404, detail="Annonce introuvable")