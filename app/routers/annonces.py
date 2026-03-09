from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter()


class AnnonceCreate(BaseModel):
    titre: str = Field(..., min_length=3, max_length=120)
    description: str = Field(..., min_length=10, max_length=500)
    prix: float = Field(..., gt=0)
    commune: str = Field(..., min_length=2, max_length=100)
    categorie: str = Field(..., min_length=2, max_length=100)


class Annonce(AnnonceCreate):
    id: int


annonces: list[Annonce] = [
    Annonce(
        id=1,
        titre="Bananes plantain fraîches",
        description="Lot de 20 bananes plantain récoltées ce matin.",
        prix=12.0,
        commune="Le Lamentin",
        categorie="Alimentation",
    ),
    Annonce(
        id=2,
        titre="Scooter 125cc occasion",
        description="Scooter en bon état, entretien à jour, idéal pour la ville.",
        prix=1600.0,
        commune="Fort-de-France",
        categorie="Transport",
    ),
    Annonce(
        id=3,
        titre="Table en bois massif",
        description="Table 6 places, fabrication artisanale locale.",
        prix=350.0,
        commune="Schoelcher",
        categorie="Maison",
    ),
    Annonce(
        id=4,
        titre="Cours de mathématiques niveau lycée",
        description="Soutien scolaire en visio ou à domicile, 2h par séance.",
        prix=40.0,
        commune="Le Robert",
        categorie="Services",
    ),
    Annonce(
        id=5,
        titre="Kayak 2 places",
        description="Kayak rigide avec pagaies, parfait pour sorties en mer calme.",
        prix=420.0,
        commune="Le Marin",
        categorie="Loisirs",
    ),
]


@router.get("/annonces", response_model=list[Annonce])
def list_annonces(
    commune: Optional[str] = Query(default=None),
    categorie: Optional[str] = Query(default=None),
) -> list[Annonce]:
    resultats = annonces

    if commune:
        resultats = [
            annonce
            for annonce in resultats
            if annonce.commune.lower() == commune.lower()
        ]

    if categorie:
        resultats = [
            annonce
            for annonce in resultats
            if annonce.categorie.lower() == categorie.lower()
        ]

    return resultats


@router.get("/annonces/{annonce_id}", response_model=Annonce)
def get_annonce(annonce_id: int) -> Annonce:
    for annonce in annonces:
        if annonce.id == annonce_id:
            return annonce

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Annonce {annonce_id} introuvable",
    )


@router.post("/annonces", response_model=Annonce, status_code=status.HTTP_201_CREATED)
def create_annonce(payload: AnnonceCreate) -> Annonce:
    next_id = max((annonce.id for annonce in annonces), default=0) + 1
    nouvelle_annonce = Annonce(id=next_id, **payload.model_dump())
    annonces.append(nouvelle_annonce)
    return nouvelle_annonce


@router.delete("/annonces/{annonce_id}", status_code=status.HTTP_200_OK)
def delete_annonce(annonce_id: int) -> dict[str, str]:
    for index, annonce in enumerate(annonces):
        if annonce.id == annonce_id:
            del annonces[index]
            return {"message": f"Annonce {annonce_id} supprimée"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Annonce {annonce_id} introuvable",
    )
