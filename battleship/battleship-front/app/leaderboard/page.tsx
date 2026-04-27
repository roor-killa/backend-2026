"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getLeaderboard, ApiError, type LeaderboardEntry } from "@/lib/api";
import Leaderboard from "@/components/Leaderboard";

export default function LeaderboardPage() {
  const [players, setPlayers] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await getLeaderboard();
        if (!cancelled) setPlayers(data);
      } catch (e) {
        if (!cancelled) setError(e instanceof ApiError ? e.message : "Erreur réseau");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="flex flex-col gap-6 py-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-ocean-light">🏆 Classement</h1>
        <Link
          href="/"
          className="rounded-lg border border-ocean/40 bg-ocean-deep/40 px-3 py-1.5 text-sm hover:border-ocean-light"
        >
          ← Accueil
        </Link>
      </div>

      {loading && <p className="text-slate-400">Chargement…</p>}
      {error && <p className="text-red-400">Erreur : {error}</p>}
      {!loading && !error && <Leaderboard players={players} />}
    </main>
  );
}
