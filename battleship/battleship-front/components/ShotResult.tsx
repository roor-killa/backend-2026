"use client";

import type { ShotResultKind } from "@/lib/api";

interface Props {
  result: ShotResultKind | null;
  /** Libellé contextuel (ex: "Ton tir", "Tir adverse") */
  label?: string;
}

/**
 * Badge pour afficher le résultat d'un tir.
 * TODO : brancher sur l'animation Unity via JSBridge (Junior).
 */
export default function ShotResult({ result, label }: Props) {
  if (!result) return null;

  const styles: Record<ShotResultKind, { bg: string; emoji: string; text: string }> = {
    hit:  { bg: "bg-hit/90 border-hit",             emoji: "💥", text: "Touché !" },
    sunk: { bg: "bg-sunk/90 border-sunk",           emoji: "🔥", text: "Coulé !" },
    miss: { bg: "bg-slate-500/80 border-slate-400", emoji: "💧", text: "À l'eau" },
  };
  const s = styles[result];

  return (
    <div
      className={`flex items-center gap-3 rounded-lg border px-4 py-3 text-white shadow-lg ${s.bg}`}
      role="status"
    >
      <span className="text-2xl">{s.emoji}</span>
      <div>
        <div className="font-bold">{s.text}</div>
        {label && <div className="text-xs opacity-80">{label}</div>}
      </div>
    </div>
  );
}
