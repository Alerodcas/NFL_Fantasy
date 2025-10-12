import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
});

export type CreateTeamPayload = {
  name: string;
  description?: string;
  logo_url?: string;
  league_id: number;
};

export async function createTeam(token: string, payload: CreateTeamPayload) {
  const { data } = await api.post("/teams", payload, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return data; // backend devuelve el objeto Team
}
