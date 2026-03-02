from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()

# Données de test — annonces caribéennes
annonces = [
    {"id": 1, "titre": "Vente mangues Julie bio", "description": "Fraîchement cueillies", "prix": 3.50, "commune": "Le Lamentin", "categorie": "alimentaire"},
    {"id": 2, "titre": "Cours de yoga face à la mer", "description": "Tous niveaux", "prix": 25.00, "commune": "Sainte-Anne", "categorie": "services"},
    {"id": 3, "titre": "Location VTT journée", "description": "Casque fourni", "prix": 15.00, "commune": "Le Morne-Rouge", "categorie": "loisirs"},
    {"id": 4, "titre": "Vente akras maison", "description": "Préparés chaque matin", "prix": 2.00, "commune": "Fort-de-France", "categorie": "alimentaire"},
    {"id": 5, "titre": "Réparation électroménager", "description": "À domicile", "prix": 50.00, "commune": "Le Robert", "categorie": "services"},
]

compteur_id = 6


# GET /annonces — liste avec filtres commune et categorie
@router.get("/annonces")
def list_annonces(
    commune: Optional[str] = Query(None, description="Filtrer par commune"),
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie")
):
    resultats = annonces.copy()

    if commune:
        resultats = [a for a in resultats if commune.lower() in a["commune"].lower()]
    if categorie:
        resultats = [a for a in resultats if a["categorie"] == categorie.lower()]

    return resultats


# GET /annonces/{id} — détail d'une annonce
@router.get("/annonces/{annonce_id}")
def get_annonce(annonce_id: int):
    for annonce in annonces:
        if annonce["id"] == annonce_id:
            return annonce
    raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")


# POST /annonces — créer une annonce
@router.post("/annonces", status_code=201)
def create_annonce(annonce: dict):
    global compteur_id
    nouvelle_annonce = {"id": compteur_id, **annonce}
    annonces.append(nouvelle_annonce)
    compteur_id += 1
    return nouvelle_annonce


# DELETE /annonces/{id} — supprimer une annonce
@router.delete("/annonces/{annonce_id}", status_code=204)
def delete_annonce(annonce_id: int):
    for i, annonce in enumerate(annonces):
        if annonce["id"] == annonce_id:
            annonces.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")
