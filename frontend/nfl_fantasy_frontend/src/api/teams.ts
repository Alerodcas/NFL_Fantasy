import axios from "axios";
import { API_BASE } from "../config/server";

const api = axios.create({
  baseURL: API_BASE,
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
