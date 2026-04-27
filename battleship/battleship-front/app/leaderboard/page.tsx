'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getLeaderboard } from '@/lib/api';

type PlayerEntry = { id: number; pseudo: string; wins: number; games_played: number };

export default function LeaderboardPage() {
  const router = useRouter();
  const [players, setPlayers] = useState<PlayerEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLeaderboard()
      .then(setPlayers)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen flex flex-col items-center p-8 gap-6">
      <h1 className="text-3xl font-bold text-blue-400">Classement</h1>

      {loading ? (
        <p className="text-slate-400">Chargement...</p>
      ) : (
        <table className="w-full max-w-lg border-collapse">
          <thead>
            <tr className="text-slate-400 text-left border-b border-slate-700">
              <th className="py-2 pr-4">#</th>
              <th className="py-2 pr-4">Pseudo</th>
              <th className="py-2 pr-4">Victoires</th>
              <th className="py-2">Parties</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p, i) => (
              <tr key={p.id} className="border-b border-slate-800">
                <td className="py-2 pr-4 text-slate-500">{i + 1}</td>
                <td className="py-2 pr-4 font-medium">{p.pseudo}</td>
                <td className="py-2 pr-4 text-green-400">{p.wins}</td>
                <td className="py-2 text-slate-400">{p.games_played}</td>
              </tr>
            ))}
            {players.length === 0 && (
              <tr>
                <td colSpan={4} className="py-4 text-center text-slate-500">Aucun joueur</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      <button
        onClick={() => router.push('/')}
        className="px-4 py-2 rounded border border-slate-600 text-slate-300 hover:bg-slate-800"
      >
        ← Retour
      </button>
    </main>
  );
}
