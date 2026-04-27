'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import { shoot, getGame } from '@/lib/api';

const UnityGame = dynamic(() => import('@/components/UnityGame'), { ssr: false });

type ShotResult = { row: number; col: number; result: 'hit' | 'miss' | 'sunk' };

export default function GamePage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const gameId = params.id as string;
  const playerId = searchParams.get('playerId');

  const [lastShotResult, setLastShotResult] = useState<ShotResult | null>(null);
  const [status, setStatus] = useState<string>('');

  const refreshGame = useCallback(async () => {
    try {
      const game = await getGame(gameId);
      setStatus(game.status ?? '');
    } catch {}
  }, [gameId]);

  useEffect(() => {
    void refreshGame();
  }, [refreshGame]);

  const onCellSelected = async (row: number, col: number) => {
    if (!playerId) return;
    try {
      const res = await shoot(gameId, row, col);
      setLastShotResult({ row, col, result: res.result });
      void refreshGame();
    } catch {}
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-4 p-4">
      <h1 className="text-2xl font-bold text-blue-400">Partie #{gameId}</h1>
      {status && <p className="text-slate-400 text-sm">Statut : {status}</p>}
      <UnityGame
        className="h-[70vh] w-full max-w-4xl"
        onCellSelected={onCellSelected}
        shotResultToSend={lastShotResult}
      />
    </main>
  );
}
