import { Howl } from "howler";

import type { ShotResultKind } from "@/lib/api";

type SoundKey = "tir" | "hit" | "miss" | "sunk" | "win";

const SOUND_CONFIG: Record<SoundKey, { src: string; volume: number }> = {
  tir: { src: "/sounds/tir.mp3", volume: 0.8 },
  hit: { src: "/sounds/hit.mp3", volume: 0.9 },
  miss: { src: "/sounds/miss.mp3", volume: 0.85 },
  sunk: { src: "/sounds/sunk.mp3", volume: 1.0 },
  win: { src: "/sounds/win.mp3", volume: 0.9 },
};

const players: Record<SoundKey, Howl> = {
  tir: new Howl({ src: [SOUND_CONFIG.tir.src], volume: SOUND_CONFIG.tir.volume, preload: true }),
  hit: new Howl({ src: [SOUND_CONFIG.hit.src], volume: SOUND_CONFIG.hit.volume, preload: true }),
  miss: new Howl({ src: [SOUND_CONFIG.miss.src], volume: SOUND_CONFIG.miss.volume, preload: true }),
  sunk: new Howl({ src: [SOUND_CONFIG.sunk.src], volume: SOUND_CONFIG.sunk.volume, preload: true }),
  win: new Howl({ src: [SOUND_CONFIG.win.src], volume: SOUND_CONFIG.win.volume, preload: true }),
};

function play(key: SoundKey): void {
  if (typeof window === "undefined") return;
  const sound = players[key];
  sound.stop();
  sound.play();
}

export function playTir(): void {
  play("tir");
}

export function playHit(): void {
  play("hit");
}

export function playMiss(): void {
  play("miss");
}

export function playSunk(): void {
  play("sunk");
}

export function playWin(): void {
  play("win");
}

export function playShotResult(result: ShotResultKind): void {
  if (result === "hit") {
    setTimeout(() => {
      playHit();
    }, 150);
  }
  else if (result === "miss") playMiss();
  else playSunk();
}
