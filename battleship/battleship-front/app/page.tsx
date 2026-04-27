'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createPlayer, createGame } from '@/lib/api';

export default function HomePage() {
  const router = useRouter();
  const [pseudo, setPseudo] = useState('');
  const [mode, setMode] = useState<'solo' | 'multi'>('solo');
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStart = async () => {
    if (!pseudo.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const player = await createPlayer(pseudo.trim());
      const game = await createGame(mode, mode === 'solo' ? difficulty : undefined);
      router.push(`/game/${game.id}?playerId=${player.id}`);
    } catch (e) {
      setError('Erreur lors de la création de la partie. Vérifiez que le backend tourne.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-8 p-8">
      <h1 className="text-4xl font-bold text-blue-400">⚓ Bataille Navale 3D</h1>

      <div className="flex flex-col gap-4 w-full max-w-sm">
        <input
          type="text"
          placeholder="Votre pseudo"
          value={pseudo}
          onChange={(e) => setPseudo(e.target.value)}
          className="px-4 py-2 rounded bg-slate-800 border border-slate-600 text-white"
        />

        <div className="flex gap-2">
          {(['solo', 'multi'] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`flex-1 py-2 rounded border ${mode === m ? 'bg-blue-600 border-blue-400' : 'bg-slate-800 border-slate-600'}`}
            >
              {m === 'solo' ? 'Solo' : 'Multijoueur'}
            </button>
          ))}
        </div>

        {mode === 'solo' && (
          <div className="flex gap-2">
            {(['easy', 'medium', 'hard'] as const).map((d) => (
              <button
                key={d}
                onClick={() => setDifficulty(d)}
                className={`flex-1 py-2 rounded border text-sm ${difficulty === d ? 'bg-blue-600 border-blue-400' : 'bg-slate-800 border-slate-600'}`}
              >
                {d === 'easy' ? 'Facile' : d === 'medium' ? 'Moyen' : 'Difficile'}
              </button>
            ))}
          </div>
        )}

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          onClick={handleStart}
          disabled={!pseudo.trim() || loading}
          className="py-3 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 font-semibold"
        >
          {loading ? 'Chargement...' : 'Jouer'}
        </button>

        <button
          onClick={() => router.push('/leaderboard')}
          className="py-2 rounded border border-slate-600 text-slate-300 hover:bg-slate-800 text-sm"
        >
          Classement
        </button>
      </div>
    </main>
  );
}
