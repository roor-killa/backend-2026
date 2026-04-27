"use client";

import type { GameMode } from "@/lib/api";

interface Props {
  value: GameMode | null;
  onChange: (mode: GameMode) => void;
  disabled?: boolean;
}

/**
 * Choix du mode de jeu : solo (contre IA) ou multiplayer (contre un autre joueur).
 * Les valeurs internes sont "solo"/"multiplayer" (alignées sur le backend).
 */
export default function ModeSelector({ value, onChange, disabled }: Props) {
  const options: { mode: GameMode; label: string; emoji: string; desc: string }[] = [
    { mode: "solo",        label: "Solo",        emoji: "🤖", desc: "Contre l'ordinateur" },
    { mode: "multiplayer", label: "Multijoueur", emoji: "👥", desc: "Contre un·e ami·e" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {options.map(({ mode, label, emoji, desc }) => {
        const active = value === mode;
        return (
          <button
            key={mode}
            onClick={() => onChange(mode)}
            disabled={disabled}
            className={[
              "rounded-xl border p-4 text-left transition",
              active
                ? "border-ocean-light bg-ocean-light/20 ring-2 ring-ocean-light"
                : "border-ocean/40 bg-ocean-deep/40 hover:border-ocean-light hover:bg-ocean-deep/70",
              disabled && "opacity-40",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            <div className="text-2xl">{emoji}</div>
            <div className="mt-1 font-semibold">{label}</div>
            <div className="text-xs text-slate-400">{desc}</div>
          </button>
        );
      })}
    </div>
  );
}
