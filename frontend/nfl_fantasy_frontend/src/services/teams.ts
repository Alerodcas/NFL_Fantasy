import api from "./apiService";

export type Team = {
  id: number;
  name: string;
  city: string;
  image_url?: string | null;
  thumbnail_url?: string | null;
  is_active: boolean;
  created_at: string;
  created_by: number;
};

export type TeamCreateJson = {
  name: string;
  city: string;
  image_url?: string; // optional
};

export type TeamUpdate = Partial<Pick<Team, "name" | "city" | "image_url" | "is_active">>;

export async function listTeams(params?: { q?: string; active?: boolean; user_id?: number }) {
  const res = await api.get<Team[]>("/teams", { params });
  return res.data;
}

export async function getTeam(id: number) {
  const res = await api.get<Team>(`/teams/${id}`);
  return res.data;
}

export async function createTeamJson(payload: TeamCreateJson) {
  const res = await api.post<Team>("/teams", payload);
  return res.data;
}

export async function createTeamUpload(payload: { name: string; city: string; file: File }) {
  const form = new FormData();
  form.append("name", payload.name);
  form.append("city", payload.city);
  form.append("image", payload.file);
  const res = await api.post<Team>("/teams/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function updateTeam(id: number, payload: TeamUpdate) {
  const res = await api.put<Team>(`/teams/${id}`, payload);
  return res.data;
}
