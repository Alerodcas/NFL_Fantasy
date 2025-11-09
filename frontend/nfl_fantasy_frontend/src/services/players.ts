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
