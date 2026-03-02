from fastapi import APIRouter, HTTPException, Query
from typing import Optional

# On crée un "routeur" pour regrouper toutes les routes liées aux annonces
router = APIRouter()

# Notre fausse base de données (en attendant le module 4 !)
annonces_db = [
    {"id": 1, "titre": "Vente mangues Julie bio", "prix": 3.50, "commune": "Le Lamentin", "categorie": "alimentaire"},
    {"id": 2, "titre": "Location Kayak", "prix": 25.00, "commune": "Le Robert", "categorie": "loisirs"},
    {"id": 3, "titre": "Cours de Maths", "prix": 20.00, "commune": "Fort-de-France", "categorie": "services"},
    {"id": 4, "titre": "Clio 3", "prix": 3200.00, "commune": "Sainte-Anne", "categorie": "vehicules"},
    {"id": 5, "titre": "T2 meublé", "prix": 650.00, "commune": "Schœlcher", "categorie": "immobilier"}
]

# Route 1 : Lister les annonces (avec filtres optionnels)
@router.get("/annonces")
def list_annonces(
    commune: Optional[str] = Query(None, description="Filtrer par commune"),
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie")
):
    resultats = annonces_db.copy()
    if commune:
        resultats = [a for a in resultats if commune.lower() in a["commune"].lower()]
    if categorie:
        resultats = [a for a in resultats if categorie.lower() == a["categorie"].lower()]
    return resultats

# Route 2 : Récupérer une seule annonce par son ID
@router.get("/annonces/{id}")
def get_annonce(id: int):
    for annonce in annonces_db:
        if annonce["id"] == id:
            return annonce
    raise HTTPException(status_code=404, detail=f"L'annonce {id} est introuvable")

# Route 3 : Créer une annonce
@router.post("/annonces", status_code=201)
def create_annonce(nouvelle_annonce: dict):
    # On génère un ID automatiquement
    nouvel_id = max([a["id"] for a in annonces_db]) + 1 if annonces_db else 1
    nouvelle_annonce["id"] = nouvel_id
    annonces_db.append(nouvelle_annonce)
    return nouvelle_annonce

# Route 4 : Supprimer une annonce
@router.delete("/annonces/{id}", status_code=204)
def delete_annonce(id: int):
    for i, annonce in enumerate(annonces_db):
        if annonce["id"] == id:
            del annonces_db[i]
            return
    raise HTTPException(status_code=404, detail=f"L'annonce {id} est introuvable")