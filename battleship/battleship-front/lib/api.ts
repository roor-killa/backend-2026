import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
});

// Players
export const createPlayer = async (pseudo: string) => {
  const { data } = await api.post('/players', { pseudo });
  return data;
};

export const getPlayer = async (id: number) => {
  const { data } = await api.get(`/players/${id}`);
  return data;
};

export const getLeaderboard = async () => {
  const { data } = await api.get('/players/leaderboard');
  return data;
};

// Games
export const createGame = async (mode: string, difficulty?: string) => {
  const { data } = await api.post('/games', { mode, difficulty });
  return data;
};

export const joinGame = async (id: string) => {
  const { data } = await api.post(`/games/${id}/join`);
  return data;
};

export const placeShips = async (id: string, ships: unknown) => {
  const { data } = await api.post(`/games/${id}/place-ships`, { ships });
  return data;
};

export const getGame = async (id: string) => {
  const { data } = await api.get(`/games/${id}`);
  return data;
};

export const getBoard = async (id: string) => {
  const { data } = await api.get(`/games/${id}/board`);
  return data;
};

// Shots
export const shoot = async (id: string, row: number, col: number) => {
  const { data } = await api.post(`/games/${id}/shoot`, { row, col });
  return data;
};

export const getShots = async (id: string) => {
  const { data } = await api.get(`/games/${id}/shots`);
  return data;
};
