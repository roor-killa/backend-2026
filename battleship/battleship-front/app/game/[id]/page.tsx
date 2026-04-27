"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  getGame,
  getBoard,
  placeShips as apiPlaceShips,
  shoot,
  getCurrentPlayerId,
  GRID_SIZE,
  CELL,
  ApiError,
  type Game,
  type BoardsPair,
  type ShipPlacement,
  type ShotResultKind,
} from "@/lib/api";
import ShipPlacer from "@/components/ShipPlacer";
import ShotResult from "@/components/ShotResult";
import { playShotResult, playTir, playWin } from "@/lib/sounds";

/**
 * Page de jeu — orchestre placement puis phase de tirs.
 *
 * Phases :
 *  1. "placement" → ShipPlacer
 *  2. "waiting"   → en attente de l'adversaire (multi)
 *  3. "playing"   → grilles + tirs
 *  4. "finished"  → écran fin de partie
 *
 * Note Junior : un <div id="unity-slot"/> est prévu pour héberger
 * <UnityGame /> qui recevra les événements via JSBridge.
 */
export default function GamePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const gameId = Number(params.id);

  const [game, setGame] = useState<Game | null>(null);
  const [boards, setBoards] = useState<BoardsPair | null>(null);
  const [lastShot, setLastShot] = useState<ShotResultKind | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const me = getCurrentPlayerId();
  // Grille précédente de ma flotte — pour détecter les tirs de l'adversaire
  const prevMyGridRef = useRef<number[][] | null>(null);
  const victoryPlayedRef = useRef(false);

  // ─── Chargement initial + rafraîchissement ─────────────────────────────────
  const refresh = useCallback(async () => {
    try {
      const g = await getGame(gameId);
      setGame(g);
      // On ne charge les grilles que si on est au moins en phase "placement"
      if (g.status !== "waiting") {
        const b = await getBoard(gameId);
        setBoards(b);
              // Détecter si l'adversaire vient de tirer sur ma grille
              if (prevMyGridRef.current) {
                const prev = prevMyGridRef.current;
                const curr = b.my_board.grid;
                let opponentHit = false;
                let opponentMiss = false;
                for (let r = 0; r < curr.length; r++) {
                  for (let c = 0; c < curr[r].length; c++) {
                    if (prev[r][c] !== curr[r][c]) {
                      if (curr[r][c] === CELL.HIT) opponentHit = true;
                      if (curr[r][c] === CELL.MISS) opponentMiss = true;
                    }
                  }
                }
                if (opponentHit) playShotResult("hit");
                else if (opponentMiss) playShotResult("miss");
              }
              // Mettre à jour la grille de référence
              prevMyGridRef.current = b.my_board.grid.map((row) => [...row]);
      }
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Erreur réseau");
    } finally {
      setLoading(false);
    }
  }, [gameId]);

  useEffect(() => {
    if (!Number.isFinite(gameId)) {
      setError("ID de partie invalide");
      setLoading(false);
      return;
    }
    if (!me) {
      router.replace("/");
      return;
    }
    refresh();
  }, [gameId, me, router, refresh]);

  // Polling toutes les 3s pour détecter l'arrivée d'un adversaire (multi)
  // ou pour rafraîchir la grille après un tir de l'IA en solo.
  useEffect(() => {
    if (!game) return;
    if (game.status === "finished") return;
    if (game.status !== "waiting" && game.mode === "solo") return;
    const it = setInterval(refresh, 3000);
    return () => clearInterval(it);
  }, [game, refresh]);

  // ─── Handlers ──────────────────────────────────────────────────────────────
  async function handlePlace(ships: ShipPlacement[]) {
    setBusy(true);
    try {
      await apiPlaceShips(gameId, ships);
    } catch (e) {
      // En cas d'erreur 400 (ex: bateaux déjà placés), on rafraîchit
      // pour afficher l'état réel sans bloquer le joueur.
      if (e instanceof ApiError && (e.status ?? 0) < 500) {
        await refresh();
        return;
      }
      setError(e instanceof ApiError ? e.message : "Erreur réseau");
      return;
    } finally {
      setBusy(false);
    }
    await refresh();
  }

  async function handleShoot(row: number, col: number) {
    if (busy || !game || game.status !== "playing") return;
    if (game.current_turn !== me) return;
    setBusy(true);
    setLastShot(null);
    try {
      playTir();
      const shotResult = await shoot(gameId, row, col);
      setLastShot(shotResult.result);

      // Son pour ton propre tir
      playShotResult(shotResult.result);

      // TODO Junior : envoyer à Unity via JSBridge
      // window.unityInstance?.SendMessage("GameManager", "OnShotResult", JSON.stringify({
      //   row, col, result: shotResult.result
      // }));

      // En solo, l'IA joue automatiquement côté backend — il suffit de
      // rafraîchir pour voir les changements dans ma grille.
      await refresh();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Erreur réseau");
    } finally {
      setBusy(false);
    }
  }

  const hasWinner = game?.winner_id != null;

  useEffect(() => {
    if (hasWinner && !victoryPlayedRef.current) {
      playWin();
      victoryPlayedRef.current = true;
    }
    if (!hasWinner) {
      victoryPlayedRef.current = false;
    }
  }, [hasWinner]);

  // ─── Rendus ────────────────────────────────────────────────────────────────
  if (loading) {
    return <p className="py-10 text-center text-slate-400">Chargement…</p>;
  }
  if (error) {
    return (
      <div className="py-10 text-center">
        <p className="text-red-400">Erreur : {error}</p>
        <Link href="/" className="mt-4 inline-block text-ocean-light underline">
          Retour à l&apos;accueil
        </Link>
      </div>
    );
  }
  if (!game) return null;

  const myTurn = game.current_turn === me;
  const iWon = game.status === "finished" && game.winner_id === me;
  const iLost = game.status === "finished" && game.winner_id !== me;

  return (
    <main className="flex flex-col gap-6 py-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ocean-light">
            Partie #{game.id}
          </h1>
          <p className="text-xs text-slate-400">
            {game.mode === "solo"
              ? `Solo — IA ${game.difficulty ?? "?"}`
              : "Multijoueur"}{" "}
            • Statut : {game.status}
          </p>
        </div>
        <Link
          href="/"
          className="rounded-lg border border-ocean/40 bg-ocean-deep/40 px-3 py-1.5 text-sm hover:border-ocean-light"
        >
          ← Accueil
        </Link>
      </header>

      {/* Slot Unity — Junior */}
      <div
        id="unity-slot"
        className="flex h-64 items-center justify-center rounded-xl border border-dashed border-ocean/40 bg-ocean-deep/20 text-sm text-slate-500"
      >
        Zone Unity WebGL (à intégrer par Junior)
      </div>

      {/* ─── Phase placement ─── */}
      {game.status === "placement" && (() => {
        const alreadyPlaced = boards?.my_board.grid.flat().some((c) => c === CELL.SHIP) ?? false;
        return alreadyPlaced ? (
          <p className="rounded-lg border border-ocean/40 bg-ocean-deep/40 p-6 text-center text-slate-300">
            Bateaux placés ✓ — En attente du démarrage de la partie…
          </p>
        ) : (
          <section className="rounded-xl border border-ocean/40 bg-ocean-deep/40 p-6">
            <h2 className="mb-4 text-lg font-semibold">Place tes bateaux</h2>
            <ShipPlacer onConfirm={handlePlace} disabled={busy} />
          </section>
        );
      })()}

      {/* ─── Phase d'attente en multi ─── */}
      {game.status === "waiting" && (
        <p className="rounded-lg border border-ocean/40 bg-ocean-deep/40 p-6 text-center text-slate-300">
          En attente d&apos;un·e adversaire… partage l&apos;ID <b>#{game.id}</b> !
        </p>
      )}

      {/* ─── Phase de jeu ─── */}
      {game.status === "playing" && boards && (
        <section className="grid gap-6 md:grid-cols-2">
          <BoardView
            title="Ma grille"
            grid={boards.my_board.grid}
            onCellClick={null}
          />
          <BoardView
            title="Grille adverse"
            grid={boards.enemy_board.grid}
            onCellClick={myTurn ? handleShoot : null}
            highlightClickable={myTurn && !busy}
          />
          <div className="md:col-span-2">
            <p className="text-center text-sm">
              {myTurn ? (
                <span className="font-semibold text-ocean-light">À toi de tirer 🎯</span>
              ) : (
                <span className="text-slate-400">Tour de l&apos;adversaire…</span>
              )}
            </p>
            <div className="mt-3 flex flex-wrap justify-center gap-3">
              <ShotResult result={lastShot} label="Ton dernier tir" />
            </div>
          </div>
        </section>
      )}

      {/* ─── Fin de partie ─── */}
      {game.status === "finished" && (
        <section className="rounded-xl border border-ocean/40 bg-ocean-deep/60 p-8 text-center">
          <h2 className="mb-2 text-3xl font-bold">
            {iWon ? "🏆 Victoire !" : iLost ? "😢 Défaite" : "Partie terminée"}
          </h2>
          <p className="text-slate-300">
            {iWon && "Bien joué, tu as coulé tous les bateaux ennemis."}
            {iLost && "Toute ta flotte a été coulée."}
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <Link
              href="/"
              className="rounded-lg bg-ocean-light px-5 py-2 font-semibold text-slate-900 hover:bg-ocean"
            >
              Rejouer
            </Link>
            <Link
              href="/leaderboard"
              className="rounded-lg border border-ocean/40 px-5 py-2 hover:border-ocean-light"
            >
              Voir le classement
            </Link>
          </div>
        </section>
      )}
    </main>
  );
}

// ─── Sous-composant : une grille 10x10 (entiers) ────────────────────────────
function BoardView({
  title,
  grid,
  onCellClick,
  highlightClickable,
}: {
  title: string;
  grid: number[][];
  onCellClick: ((row: number, col: number) => void) | null;
  highlightClickable?: boolean;
}) {
  const safeGrid: number[][] =
    grid?.length === GRID_SIZE
      ? grid
      : Array.from({ length: GRID_SIZE }, () =>
          Array.from({ length: GRID_SIZE }, () => CELL.EMPTY),
        );

  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-slate-300">{title}</h3>
      <div
        className="grid gap-0.5 rounded-lg border border-ocean/40 bg-ocean-deep/40 p-2"
        style={{ gridTemplateColumns: `repeat(${GRID_SIZE}, minmax(0, 1fr))` }}
      >
        {safeGrid.flatMap((line, row) =>
          line.map((cell, col) => {
            let cls = "bg-slate-800";
            if (cell === CELL.SHIP) cls = "bg-ocean-light";
            else if (cell === CELL.HIT) cls = "bg-hit";
            else if (cell === CELL.MISS) cls = "bg-miss";

            const alreadyShot = cell === CELL.HIT || cell === CELL.MISS;
            const clickable = onCellClick && !alreadyShot;
            return (
              <button
                key={`${row}-${col}`}
                onClick={() => clickable && onCellClick(row, col)}
                disabled={!clickable}
                className={[
                  "aspect-square h-7 w-7 rounded transition",
                  cls,
                  clickable && highlightClickable
                    ? "hover:ring-2 hover:ring-ocean-light"
                    : "cursor-default",
                ].join(" ")}
                aria-label={`Case ${row},${col}`}
              />
            );
          }),
        )}
      </div>
    </div>
  );
}
