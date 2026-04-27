"use client";

import type { Difficulty } from "@/lib/api";

interface Props {
  value: Difficulty | null;
  onChange: (d: Difficulty) => void;
  disabled?: boolean;
}

/**
 * Choix du niveau de l'IA — utilisé uniquement en mode solo.
 * Les valeurs internes sont "easy"/"medium"/"hard" (attendues par le backend),
 * mais on affiche des libellés en français.
 */
export default function DifficultySelector({ value, onChange, disabled }: Props) {
  const options: { key: Difficulty; label: string; emoji: string; hint: string }[] = [
    { key: "easy",   label: "Facile",    emoji: "🟢", hint: "Tirs aléatoires" },
    { key: "medium", label: "Moyen",     emoji: "🟡", hint: "Cible les cases adjacentes après un touché" },
    { key: "hard",   label: "Difficile", emoji: "🔴", hint: "Carte de probabilités" },
  ];

  return (
    <div className="grid grid-cols-3 gap-2">
      {options.map(({ key, label, emoji, hint }) => {
        const active = value === key;
        return (
          <button
            key={key}
            onClick={() => onChange(key)}
            disabled={disabled}
            title={hint}
            className={[
              "rounded-lg border px-3 py-2 text-sm transition",
              active
                ? "border-ocean-light bg-ocean-light/20 ring-2 ring-ocean-light"
                : "border-ocean/40 bg-ocean-deep/40 hover:border-ocean-light",
              disabled && "opacity-40",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            <div>{emoji}</div>
            <div className="font-medium">{label}</div>
          </button>
        );
      })}
    </div>
  );
}
