import api from "./apiService";

export type Player = {
  id: number;
  name: string;
  position: string;
  image_url?: string | null;
  thumbnail_url?: string | null;
  is_active: boolean;
  created_at: string;
  created_by: number;
  team_id: number;
};

export type PlayerCreateJson = {
  name: string;
  position: string;
  team_id: number;
  image_url: string; // required for JSON create
};

export async function createPlayerJson(payload: PlayerCreateJson) {
  const res = await api.post<Player>("/players", payload);
  return res.data;
}

export async function createPlayerUpload(payload: { name: string; position: string; team_id: number; file: File }) {
  const form = new FormData();
  form.append("name", payload.name);
  form.append("position", payload.position);
  form.append("team_id", String(payload.team_id));
  form.append("image", payload.file);

  const res = await api.post<Player>("/players/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

// Player news types and API
export type PlayerNews = {
  id: number;
  player_id: number;
  author_id: number;
  summary: string;
  text: string;
  is_injury: boolean;
  injury_type?: string | null;
  changes?: Record<string, any> | null;
  created_at: string;
};

export type PlayerNewsCreate = {
  player_id: number;
  summary: string;
  text: string;
  is_injury?: boolean;
  injury_type?: string | null;
  changes?: Record<string, any> | null;
  update_state?: boolean;
};

export async function getPlayer(playerId: number) {
  const res = await api.get<Player>(`/players/${playerId}`);
  return res.data;
}

export async function getPlayerNews(playerId: number) {
  const res = await api.get<PlayerNews[]>(`/players/${playerId}/news`);
  return res.data;
}

export async function createPlayerNews(playerId: number, payload: PlayerNewsCreate) {
  const res = await api.post<PlayerNews>(`/players/${playerId}/news`, payload);
  return res.data;
}

export async function listPlayersByTeam(teamId: number) {
  const res = await api.get<Player[]>(`/players`, { params: { team_id: teamId } });
  return res.data;
}
