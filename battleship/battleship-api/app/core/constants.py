# ── Grille ─────────────────────────────────────────────
GRID_SIZE = 10  # Grille de 10x10

# ── Bateaux disponibles ────────────────────────────────
# Chaque bateau : nom → taille en cases
SHIPS = {
    "carrier":    5,  # Porte-avions
    "cruiser":    4,  # Croiseur
    "destroyer":  3,  # Destroyer
    "submarine":  3,  # Sous-marin
    "torpedo":    2,  # Torpilleur
}

# ── Résultats d'un tir ─────────────────────────────────
class ShotResult:
    MISS  = "miss"   # À l'eau
    HIT   = "hit"    # Touché
    SUNK  = "sunk"   # Coulé

# ── Statuts d'une partie ───────────────────────────────
class GameStatus:
    WAITING    = "waiting"    # En attente du 2ème joueur (multijoueur)
    PLACEMENT  = "placement"  # Phase de placement des bateaux
    PLAYING    = "playing"    # Partie en cours
    FINISHED   = "finished"   # Partie terminée

# ── Modes de jeu ───────────────────────────────────────
class GameMode:
    SOLO        = "solo"
    MULTIPLAYER = "multiplayer"

# ── Niveaux de difficulté IA ───────────────────────────
class Difficulty:
    EASY   = "easy"    # Tirs aléatoires
    MEDIUM = "medium"  # Cible les cases adjacentes après touché
    HARD   = "hard"    # Carte de probabilités

# ── Orientations des bateaux ───────────────────────────
class Orientation:
    HORIZONTAL = "horizontal"
    VERTICAL   = "vertical"