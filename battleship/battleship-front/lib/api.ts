/**
 * ============================================================================
 *  Bataille Navale 3D — Couche API
 * ============================================================================
 *
 *  Ce fichier centralise TOUS les appels HTTP vers le backend FastAPI
 *  d'Ibrahim (battleship-api). Aucune autre partie du frontend ne doit
 *  appeler l'API directement : toujours passer par les fonctions ci-dessous.
 *
 *  Base URL configurée via la variable d'environnement NEXT_PUBLIC_API_URL
 *  (cf. .env.example).
 *
 *  Auteur : Mohand Sadi
 * ============================================================================
 */

import axios, { AxiosError, AxiosInstance } from "axios";

// ─── Configuration de base ──────────────────────────────────────────────────

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10_000,
});

// Intercepteur : uniformise les erreurs renvoyées par FastAPI
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string | Array<{ msg: string; loc?: string[] }> }>) => {
    const detail = error.response?.data?.detail;
    let message = "Erreur inconnue";

    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail) && detail[0]?.msg) {
      // Pydantic renvoie une liste — on formate joliment
      message = detail
        .map((d) => {
          const field = d.loc?.filter((x) => x !== "body").join(".");
          return field ? `${field} : ${d.msg}` : d.msg;
        })
        .join(" | ");
    } else if (error.message) {
      message = error.message;
    }

    return Promise.reject(new ApiError(message, error.response?.status));
  },
);

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// ─── Types partagés — alignés sur app/core/constants.py ─────────────────────

export type GameMode = "solo" | "multiplayer";
export type Difficulty = "easy" | "medium" | "hard";
export type GameStatus = "waiting" | "placement" | "playing" | "finished";
export type ShotResultKind = "hit" | "miss" | "sunk";
export type Orientation = "horizontal" | "vertical";

/** 5 types de bateaux définis côté backend. */
export type ShipType =
  | "carrier"     // Porte-avions — 5 cases
  | "cruiser"     // Croiseur    — 4 cases
  | "destroyer"   // Destroyer   — 3 cases
  | "submarine"   // Sous-marin  — 3 cases
  | "torpedo";    // Torpilleur  — 2 cases

/** Valeurs entières utilisées dans les grilles renvoyées par le backend. */
export const CELL = {
  EMPTY: 0,
  SHIP:  1,
  HIT:   2,
  MISS:  3,
} as const;

export interface Position {
  row: number; // 0..9
  col: number; // 0..9
}

export interface Player {
  id: number;
  pseudo: string;
  score: number;
  games_played: number;
  created_at: string; // ISO 8601
}

/** Entrée retournée par /players/leaderboard (inclut un rank). */
export interface LeaderboardEntry {
  rank: number;
  id: number;
  pseudo: string;
  score: number;
  games_played: number;
}

/** Format attendu par POST /games/{id}/place-ships pour chaque bateau. */
export interface ShipPlacement {
  type: ShipType;
  row: number;
  col: number;
  orientation: Orientation;
}

export interface Board {
  player_id: number;
  grid: number[][]; // 10x10 d'entiers (cf. CELL)
}

export interface BoardsPair {
  my_board: Board;
  enemy_board: Board; // grille adverse avec bateaux masqués
}

export interface Game {
  id: number;
  mode: GameMode;
  difficulty: Difficulty | null;
  status: GameStatus;
  current_turn: number | null;
  winner_id: number | null;
}

export interface Shot {
  id: number;
  game_id: number;
  player_id: number;
  row: number;
  col: number;
  result: ShotResultKind;
  created_at: string;
  game_over: boolean;
  winner_id: number | null;
}

export interface ShotHistory {
  shots: Shot[];
  total: number;
}

// ─── Helpers locaux ─────────────────────────────────────────────────────────

/** Récupère l'ID du joueur connecté depuis le localStorage. */
export function getCurrentPlayerId(): number | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem("battleship_player_id");
  return raw ? Number(raw) : null;
}

export function setCurrentPlayerId(id: number): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem("battleship_player_id", String(id));
}

export function clearCurrentPlayer(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("battleship_player_id");
}

// ─── Joueurs ────────────────────────────────────────────────────────────────

/** POST /players/ — crée un joueur avec un pseudo. */
export async function createPlayer(pseudo: string): Promise<Player> {
  const { data } = await api.post<Player>("/players/", { pseudo });
  return data;
}

/** GET /players/{id} — récupère un joueur par son ID. */
export async function getPlayer(id: number): Promise<Player> {
  const { data } = await api.get<Player>(`/players/${id}`);
  return data;
}

/** GET /players/leaderboard — classement trié par score. */
export async function getLeaderboard(limit = 10): Promise<LeaderboardEntry[]> {
  const { data } = await api.get<LeaderboardEntry[]>("/players/leaderboard", {
    params: { limit },
  });
  return data;
}

// ─── Parties ────────────────────────────────────────────────────────────────

/**
 * POST /games/?player_id=X — crée une nouvelle partie.
 *  - `player_id` est envoyé en query param (exigé par le backend)
 *  - en mode solo, la difficulté est obligatoire
 */
export async function createGame(
  mode: GameMode,
  difficulty?: Difficulty,
): Promise<Game> {
  const playerId = getCurrentPlayerId();
  if (!playerId) {
    throw new ApiError("Aucun joueur connecté — créer d'abord un pseudo.");
  }
  const body: Record<string, unknown> = { mode };
  if (mode === "solo") body.difficulty = difficulty ?? "easy";

  const { data } = await api.post<Game>("/games/", body, {
    params: { player_id: playerId },
  });
  return data;
}

/** POST /games/{id}/join — rejoindre une partie multijoueur existante. */
export async function joinGame(gameId: number): Promise<Game> {
  const playerId = getCurrentPlayerId();
  if (!playerId) {
    throw new ApiError("Aucun joueur connecté.");
  }
  const { data } = await api.post<Game>(`/games/${gameId}/join`, {
    player_id: playerId,
  });
  return data;
}

/** POST /games/{id}/place-ships — place les 5 bateaux du joueur courant. */
export async function placeShips(
  gameId: number,
  ships: ShipPlacement[],
): Promise<Game> {
  const playerId = getCurrentPlayerId();
  if (!playerId) {
    throw new ApiError("Aucun joueur connecté.");
  }
  const { data } = await api.post<Game>(`/games/${gameId}/place-ships`, {
    player_id: playerId,
    ships,
  });
  return data;
}

/** GET /games/{id} — état complet de la partie. */
export async function getGame(gameId: number): Promise<Game> {
  const { data } = await api.get<Game>(`/games/${gameId}`);
  return data;
}

/** GET /games/{id}/board?player_id=X — les deux grilles. */
export async function getBoard(gameId: number): Promise<BoardsPair> {
  const playerId = getCurrentPlayerId();
  if (!playerId) {
    throw new ApiError("Aucun joueur connecté.");
  }
  const { data } = await api.get<BoardsPair>(`/games/${gameId}/board`, {
    params: { player_id: playerId },
  });
  return data;
}

// ─── Tirs ───────────────────────────────────────────────────────────────────

/**
 * POST /games/{id}/shoot — tirer sur une case.
 * En mode solo, l'IA rejoue automatiquement derrière : son tir n'est PAS
 * renvoyé dans la réponse, il faut refaire un GET /board pour voir la maj.
 */
export async function shoot(
  gameId: number,
  row: number,
  col: number,
): Promise<Shot> {
  const playerId = getCurrentPlayerId();
  if (!playerId) {
    throw new ApiError("Aucun joueur connecté.");
  }
  if (row < 0 || row > 9 || col < 0 || col > 9) {
    throw new ApiError("Coordonnées hors de la grille (0..9).");
  }
  const { data } = await api.post<Shot>(`/games/${gameId}/shoot`, {
    player_id: playerId,
    row,
    col,
  });
  return data;
}

/** GET /games/{id}/shots — historique complet des tirs. */
export async function getShots(gameId: number): Promise<ShotHistory> {
  const { data } = await api.get<ShotHistory>(`/games/${gameId}/shots`);
  return data;
}

// ─── Constantes utilitaires ─────────────────────────────────────────────────

/** Flotte standard — 5 bateaux, 17 cases au total (alignée sur constants.py). */
export const FLEET: { type: ShipType; size: number; label: string }[] = [
  { type: "carrier",   size: 5, label: "Porte-avions" },
  { type: "cruiser",   size: 4, label: "Croiseur" },
  { type: "destroyer", size: 3, label: "Destroyer" },
  { type: "submarine", size: 3, label: "Sous-marin" },
  { type: "torpedo",   size: 2, label: "Torpilleur" },
];

export const GRID_SIZE = 10;
