"use client";

import type { LeaderboardEntry } from "@/lib/api";
import { getCurrentPlayerId } from "@/lib/api";

interface Props {
  players: LeaderboardEntry[];
}

/**
 * Tableau du classement — met en évidence la ligne du joueur courant.
 */
export default function Leaderboard({ players }: Props) {
  const me = getCurrentPlayerId();

  if (players.length === 0) {
    return (
      <p className="rounded-lg border border-ocean/40 bg-ocean-deep/40 p-6 text-center text-slate-400">
        Aucun joueur pour le moment.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-ocean/40 bg-ocean-deep/40">
      <table className="w-full text-left text-sm">
        <thead className="bg-ocean-deep/80 text-xs uppercase text-slate-400">
          <tr>
            <th className="px-4 py-3">#</th>
            <th className="px-4 py-3">Pseudo</th>
            <th className="px-4 py-3 text-right">Score</th>
            <th className="px-4 py-3 text-right">Parties</th>
          </tr>
        </thead>
        <tbody>
          {players.map((p) => {
            const isMe = me !== null && p.id === me;
            return (
              <tr
                key={p.id}
                className={[
                  "border-t border-ocean/20",
                  isMe ? "bg-ocean-light/20 font-semibold" : "hover:bg-ocean-deep/80",
                ].join(" ")}
              >
                <td className="px-4 py-3">
                  {p.rank === 1 ? "🥇" : p.rank === 2 ? "🥈" : p.rank === 3 ? "🥉" : p.rank}
                </td>
                <td className="px-4 py-3">
                  {p.pseudo}
                  {isMe && <span className="ml-2 text-xs text-ocean-light">(toi)</span>}
                </td>
                <td className="px-4 py-3 text-right">{p.score}</td>
                <td className="px-4 py-3 text-right text-slate-400">{p.games_played}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
