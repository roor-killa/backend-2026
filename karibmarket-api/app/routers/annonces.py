from fastapi import APIRouter

router = APIRouter()

annonces = [
    {"id":1,"titre":"Mangues bio","prix":3.5,"commune":"Le Lamentin"},
    {"id":2,"titre":"Cours de yoga","prix":20,"commune":"Sainte-Anne"}
]

@router.get("/annonces")
def list_annonces():
    return annonces


@router.get("/annonces/{id}")
def get_annonce(id:int):

    for annonce in annonces:
        if annonce["id"] == id:
            return annonce

    return {"error":"Annonce introuvable"}