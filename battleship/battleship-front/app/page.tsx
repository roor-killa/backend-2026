"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  createPlayer,
  createGame,
  joinGame,
  getPlayer,
  setCurrentPlayerId,
  getCurrentPlayerId,
  clearCurrentPlayer,
  ApiError,
  type GameMode,
  type Difficulty,
} from "@/lib/api";
import ModeSelector from "@/components/ModeSelector";
import DifficultySelector from "@/components/DifficultySelector";

type Step = "pseudo" | "mode" | "difficulty" | "join";

/**
 * Page d'accueil — flow complet :
 *   1. Pseudo
 *   2. Mode (solo/multiplayer)
 *   3. Difficulté (solo) OU choix créer/rejoindre (multi)
 *   4. Création de partie → redirection vers /game/{id}
 *
 * NOTE : on démarre toujours sur "pseudo" pour éviter les erreurs
 * d'hydration (localStorage n'existe pas côté serveur). Un useEffect
 * bascule ensuite sur "mode" si un joueur est déjà connecté.
 */
export default function HomePage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("pseudo");

  useEffect(() => {
    // Toujours repartir du pseudo pour ne pas sauter l'étape d'identification
    clearCurrentPlayer();
    setStep("pseudo");
  }, []);
  const [pseudo, setPseudo] = useState("");
  const [mode, setMode] = useState<GameMode | null>(null);
  const [difficulty, setDifficulty] = useState<Difficulty | null>(null);
  const [joinId, setJoinId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handlePseudo() {
    if (!pseudo.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const p = await createPlayer(pseudo.trim());
      setCurrentPlayerId(p.id);
      setStep("mode");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Erreur réseau");
    } finally {
      setBusy(false);
    }
  }

  function handleModeChoice(m: GameMode) {
    setMode(m);
    setStep(m === "solo" ? "difficulty" : "join");
  }

  async function handleStartSolo() {
    if (!difficulty) return;
    setBusy(true);
    setError(null);
    try {
      const g = await createGame("solo", difficulty);
      router.push(`/game/${g.id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Erreur réseau");
      setBusy(false);
    }
  }

  async function handleCreateMulti() {
    setBusy(true);
    setError(null);
    try {
      const g = await createGame("multiplayer");
      router.push(`/game/${g.id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Erreur réseau");
      setBusy(false);
    }
  }

  async function handleJoinMulti() {
    const id = Number(joinId);
    if (!Number.isFinite(id) || id <= 0) {
      setError("ID invalide");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const g = await joinGame(id);
      router.push(`/game/${g.id}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Erreur réseau");
      setBusy(false);
    }
  }

  return (
    <main className="flex flex-col items-center gap-8 py-12">
      <header className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-ocean-light">
          🚢 Bataille Navale 3D
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Université des Antilles — L2 Informatique
        </p>
      </header>

      <section className="w-full max-w-md rounded-xl border border-ocean/40 bg-ocean-deep/60 p-6 shadow-lg backdrop-blur">
        {step === "pseudo" && (
          <>
            <h2 className="mb-4 text-xl font-semibold">Choisis ton pseudo</h2>
            <div className="flex gap-2">
              <input
                type="text"
                value={pseudo}
                onChange={(e) => setPseudo(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handlePseudo()}
                placeholder="Ton pseudo"
                maxLength={20}
                className="flex-1 rounded-lg border border-ocean/60 bg-slate-900/80 px-3 py-2 outline-none focus:border-ocean-light"
              />
              <button
                onClick={handlePseudo}
                disabled={busy || !pseudo.trim()}
                className="rounded-lg bg-ocean-light px-4 py-2 font-medium text-slate-900 transition hover:bg-ocean disabled:opacity-40"
              >
                {busy ? "..." : "Suivant"}
              </button>
            </div>
          </>
        )}

        {step === "mode" && (
          <>
            <h2 className="mb-4 text-xl font-semibold">Mode de jeu</h2>
            <ModeSelector value={mode} onChange={handleModeChoice} disabled={busy} />
          </>
        )}

        {step === "difficulty" && (
          <>
            <h2 className="mb-4 text-xl font-semibold">Niveau de l&apos;IA</h2>
            <DifficultySelector
              value={difficulty}
              onChange={setDifficulty}
              disabled={busy}
            />
            <div className="mt-6 flex justify-between">
              <button
                onClick={() => setStep("mode")}
                className="text-sm text-slate-400 hover:text-ocean-light"
              >
                ← Retour
              </button>
              <button
                onClick={handleStartSolo}
                disabled={busy || !difficulty}
                className="rounded-lg bg-ocean-light px-5 py-2 font-semibold text-slate-900 hover:bg-ocean disabled:opacity-40"
              >
                {busy ? "Création…" : "Commencer"}
              </button>
            </div>
          </>
        )}

        {step === "join" && (
          <>
            <h2 className="mb-4 text-xl font-semibold">Multijoueur</h2>
            <button
              onClick={handleCreateMulti}
              disabled={busy}
              className="w-full rounded-lg bg-ocean-light px-4 py-3 font-semibold text-slate-900 hover:bg-ocean disabled:opacity-40"
            >
              Créer une partie
            </button>
            <div className="my-4 flex items-center gap-3 text-xs text-slate-500">
              <div className="h-px flex-1 bg-ocean/30" />
              ou
              <div className="h-px flex-1 bg-ocean/30" />
            </div>
            <div className="flex gap-2">
              <input
                type="number"
                value={joinId}
                onChange={(e) => setJoinId(e.target.value)}
                placeholder="ID de la partie"
                className="flex-1 rounded-lg border border-ocean/60 bg-slate-900/80 px-3 py-2 outline-none focus:border-ocean-light"
              />
              <button
                onClick={handleJoinMulti}
                disabled={busy || !joinId}
                className="rounded-lg border border-ocean/40 bg-ocean-deep/40 px-4 py-2 font-medium hover:border-ocean-light disabled:opacity-40"
              >
                Rejoindre
              </button>
            </div>
            <button
              onClick={() => setStep("mode")}
              className="mt-4 text-sm text-slate-400 hover:text-ocean-light"
            >
              ← Retour
            </button>
          </>
        )}

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
      </section>

      <Link
        href="/leaderboard"
        className="text-sm text-slate-400 underline hover:text-ocean-light"
      >
        🏆 Voir le classement
      </Link>
    </main>
  );
}
