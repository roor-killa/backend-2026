"""
Ti Punch Master — Backend FastAPI
Version 2.0 · Martinique 2026
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ScoreRequest, ScoreResponse, LeaderboardEntry, LeaderboardPost
from typing import List
import json, os, math
from datetime import datetime

app = FastAPI(
    title="Ti Punch Master API",
    description="Backend de scoring et classement pour Ti Punch Master",
    version="2.0.0"
)

# CORS — autorise Unity (localhost) et navigateurs locaux
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Chargement des données ───────────────────────────────────────────────────

BASE_DIR = os.path.dirname(__file__)
CLIENTS_FILE     = os.path.join(BASE_DIR, "data", "clients.json")
LEADERBOARD_FILE = os.path.join(BASE_DIR, "data", "leaderboard.json")

def load_json(path: str) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_leaderboard() -> list:
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    return load_json(LEADERBOARD_FILE)

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Ti Punch Master API v2.0 — Bienvenue au bar !"}


@app.get("/clients")
def get_clients():
    """Retourne la liste des 12 clients avec leurs recettes cibles."""
    clients = load_json(CLIENTS_FILE)
    return {"clients": clients, "count": len(clients)}


@app.get("/clients/{client_id}")
def get_client(client_id: str):
    """Retourne un client spécifique par son identifiant."""
    clients = load_json(CLIENTS_FILE)
    client = next((c for c in clients if c["id"] == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' introuvable")
    return client


@app.post("/score", response_model=ScoreResponse)
def calculate_score(req: ScoreRequest):
    """
    Calcule le score pour un service.

    Payload :
        client_id : str
        cocktail  : str
        dosages   : dict[str, float]  — ex: {"rhum": 5, "citron": 3, "sucre": 2}

    Retourne :
        score    : int
        feedback : str
        target   : dict[str, float]
        diffs    : dict[str, float]
    """
    clients = load_json(CLIENTS_FILE)
    client  = next((c for c in clients if c["id"] == req.client_id), None)

    if not client:
        raise HTTPException(status_code=404, detail=f"Client '{req.client_id}' introuvable")

    recipe  = client["recipes"].get(req.cocktail)
    if not recipe:
        raise HTTPException(status_code=400,
            detail=f"Cocktail '{req.cocktail}' non défini pour ce client")

    target    = recipe["target"]      # {"rhum": 4, "citron": 3, "sucre": 3}
    tolerance = recipe["tolerance"]   # float — ex: 1.0 ou 0.5

    # Calcul des écarts
    diffs = {}
    total_diff = 0.0
    for ingredient, target_cl in target.items():
        actual_cl  = req.dosages.get(ingredient, 0.0)
        diff       = abs(actual_cl - target_cl)
        diffs[ingredient] = round(diff, 2)
        total_diff += diff

    total_diff = round(total_diff, 2)

    # Barème de score (cahier des charges §5.3)
    if total_diff == 0:
        score = 100
    elif total_diff <= tolerance:
        score = 85
    elif total_diff <= tolerance * 2:
        score = 65
    elif total_diff <= tolerance * 3 + 1:
        score = 40
    elif total_diff <= tolerance * 4 + 2:
        score = 20
    else:
        score = 5

    # Feedback textuel selon score
    feedback_map = {
        100: "Parfait ! Exactement ce qu'il me faut, magnifique !",
        85:  "Très bon, bravo ! C'est presque parfait.",
        65:  "Pas mal, ça passe... mais on peut faire mieux !",
        40:  "Mouais... le dosage est un peu approximatif.",
        20:  "Bof, c'est raté mon ami. Essaie encore.",
        5:   "Non, non, non... c'est quoi ça ?! Tu appelles ça un cocktail ?!",
    }
    feedback = feedback_map.get(score, feedback_map[5])

    return ScoreResponse(
        score=score,
        feedback=feedback,
        target=target,
        diffs=diffs,
        total_diff=total_diff
    )


@app.get("/leaderboard")
def get_leaderboard():
    """Retourne le top 5 des meilleurs scores."""
    lb = load_leaderboard()
    top5 = sorted(lb, key=lambda x: x["score"], reverse=True)[:5]
    return {"leaderboard": top5, "count": len(top5)}


@app.post("/leaderboard")
def post_leaderboard(entry: LeaderboardPost):
    """Enregistre un score de fin de partie dans le classement."""
    lb = load_leaderboard()
    new_entry = {
        "player_name": entry.player_name,
        "score":       entry.score,
        "date":        datetime.now().strftime("%d/%m/%Y"),
        "timestamp":   datetime.now().isoformat(),
    }
    lb.append(new_entry)
    lb = sorted(lb, key=lambda x: x["score"], reverse=True)[:100]  # garde top 100
    save_json(LEADERBOARD_FILE, lb)
    rank = next(i + 1 for i, e in enumerate(lb) if e["timestamp"] == new_entry["timestamp"])
    return {"message": "Score enregistré", "rank": rank, "entry": new_entry}


@app.delete("/leaderboard")
def reset_leaderboard():
    """Remet le classement à zéro (admin)."""
    save_json(LEADERBOARD_FILE, [])
    return {"message": "Classement réinitialisé"}
