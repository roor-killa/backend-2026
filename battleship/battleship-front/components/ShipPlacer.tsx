"use client";

import { useMemo, useState } from "react";
import {
  FLEET,
  GRID_SIZE,
  type Orientation,
  type Position,
  type ShipPlacement,
} from "@/lib/api";

interface Props {
  onConfirm: (ships: ShipPlacement[]) => void | Promise<void>;
  disabled?: boolean;
}

/**
 * Interface de placement des bateaux sur une grille 10x10.
 *
 *  - clic sur une case → pose le bateau courant (ancre = case cliquée)
 *  - bouton "Pivoter"  → change horizontal/vertical
 *  - bouton "Reset"    → efface tous les placements
 *  - bouton "Valider"  → appelle onConfirm avec les 5 bateaux placés
 *
 *  Le format envoyé est { type, row, col, orientation } — celui attendu par
 *  le backend FastAPI d'Ibrahim.
 */
export default function ShipPlacer({ onConfirm, disabled }: Props) {
  const [placed, setPlaced] = useState<ShipPlacement[]>([]);
  const [orientation, setOrientation] = useState<Orientation>("horizontal");
  const [hover, setHover] = useState<Position | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const nextShip = FLEET[placed.length]; // undefined = tous posés

  // ─── Occupation : toutes les cases déjà prises par les bateaux posés ──────
  const occupied = useMemo(() => {
    const set = new Set<string>();
    for (const s of placed) {
      const size = FLEET.find((f) => f.type === s.type)?.size ?? 0;
      for (let i = 0; i < size; i++) {
        const r = s.row + (s.orientation === "vertical" ? i : 0);
        const c = s.col + (s.orientation === "horizontal" ? i : 0);
        set.add(`${r}-${c}`);
      }
    }
    return set;
  }, [placed]);

  // ─── Prévisualisation (cases que le bateau courant occuperait) ────────────
  const candidate = useMemo<Position[] | null>(() => {
    if (!hover || !nextShip) return null;
    const positions: Position[] = [];
    for (let i = 0; i < nextShip.size; i++) {
      positions.push({
        row: hover.row + (orientation === "vertical" ? i : 0),
        col: hover.col + (orientation === "horizontal" ? i : 0),
      });
    }
    return positions;
  }, [hover, orientation, nextShip]);

  const candidateValid = useMemo(() => {
    if (!candidate) return false;
    return candidate.every(
      (p) =>
        p.row >= 0 &&
        p.row < GRID_SIZE &&
        p.col >= 0 &&
        p.col < GRID_SIZE &&
        !occupied.has(`${p.row}-${p.col}`),
    );
  }, [candidate, occupied]);

  // ─── Handlers ─────────────────────────────────────────────────────────────
  function place(row: number, col: number) {
    if (!nextShip || !candidateValid) return;
    setPlaced((prev) => [
      ...prev,
      { type: nextShip.type, row, col, orientation },
    ]);
  }

  function reset() {
    setPlaced([]);
  }

  async function confirm() {
    if (placed.length !== FLEET.length) return;
    setSubmitting(true);
    try {
      await onConfirm(placed);
    } finally {
      setSubmitting(false);
    }
  }

  // ─── Rendu ────────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col items-center gap-4">
      {/* Barre d'infos */}
      <div className="flex w-full flex-wrap items-center justify-between gap-2">
        <div className="text-sm">
          {nextShip ? (
            <>
              À placer :{" "}
              <span className="font-semibold text-ocean-light">
                {nextShip.label}
              </span>{" "}
              <span className="text-slate-400">({nextShip.size} cases)</span>
            </>
          ) : (
            <span className="font-semibold text-emerald-400">
              Tous les bateaux sont placés ✓
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() =>
              setOrientation((o) =>
                o === "horizontal" ? "vertical" : "horizontal",
              )
            }
            disabled={disabled || !nextShip}
            className="rounded border border-ocean/40 bg-ocean-deep/40 px-3 py-1 text-sm hover:border-ocean-light disabled:opacity-40"
          >
            Pivoter ({orientation === "horizontal" ? "→" : "↓"})
          </button>
          <button
            onClick={reset}
            disabled={disabled || placed.length === 0}
            className="rounded border border-ocean/40 bg-ocean-deep/40 px-3 py-1 text-sm hover:border-ocean-light disabled:opacity-40"
          >
            Réinitialiser
          </button>
        </div>
      </div>

      {/* Grille */}
      <div
        className="grid gap-0.5 rounded-lg border border-ocean/40 bg-ocean-deep/40 p-2"
        style={{ gridTemplateColumns: `repeat(${GRID_SIZE}, minmax(0, 1fr))` }}
        onMouseLeave={() => setHover(null)}
      >
        {Array.from({ length: GRID_SIZE * GRID_SIZE }).map((_, idx) => {
          const row = Math.floor(idx / GRID_SIZE);
          const col = idx % GRID_SIZE;
          const isPlaced = occupied.has(`${row}-${col}`);
          const inCandidate = candidate?.some(
            (p) => p.row === row && p.col === col,
          );
          let cls = "bg-slate-800 hover:bg-slate-700";
          if (isPlaced) cls = "bg-ocean-light";
          else if (inCandidate)
            cls = candidateValid ? "bg-emerald-500/60" : "bg-red-500/60";

          return (
            <button
              key={idx}
              onMouseEnter={() => setHover({ row, col })}
              onClick={() => place(row, col)}
              disabled={disabled || !nextShip}
              className={`aspect-square h-8 w-8 rounded transition ${cls} disabled:cursor-default`}
              aria-label={`Case ${row},${col}`}
            />
          );
        })}
      </div>

      {/* Liste des bateaux */}
      <ul className="flex w-full flex-wrap gap-2 text-xs">
        {FLEET.map((f, i) => (
          <li
            key={f.type}
            className={`rounded border px-2 py-1 ${
              i < placed.length
                ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-300"
                : i === placed.length
                  ? "border-ocean-light bg-ocean-light/10 text-ocean-light"
                  : "border-ocean/40 text-slate-400"
            }`}
          >
            {i < placed.length ? "✓ " : ""}
            {f.label} ({f.size})
          </li>
        ))}
      </ul>

      <button
        onClick={confirm}
        disabled={disabled || submitting || placed.length !== FLEET.length}
        className="rounded-lg bg-ocean-light px-6 py-2 font-semibold text-slate-900 transition hover:bg-ocean disabled:opacity-40"
      >
        {submitting ? "Envoi…" : "Valider le placement"}
      </button>
    </div>
  );
}
