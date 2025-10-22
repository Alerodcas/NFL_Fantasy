// frontend/nfl_fantasy_frontend/src/services/leagues.ts
import api from "./apiService";

export type LeagueCreatePayload = {
  name: string;
  description?: string;
  max_teams: 4|6|8|10|12|14|16|18|20;
  password: string;          // 8–12 alphanumeric, at least one lower + one upper
  playoff_format: 4|6;
  allow_decimal_scoring: boolean;
  team_name: string;
};

export type LeagueCreatedResponse = {
  id: number;
  uuid?: string;
  name: string;
  status: string;
  max_teams: number;
  playoff_format: number;
  allow_decimal_scoring: boolean;
  season_id: number;
  slots_remaining: number;
  commissioner_team_id?: number; // present if backend returns it
};

export async function createLeague(payload: LeagueCreatePayload) {
  const res = await api.post<LeagueCreatedResponse>("/leagues", payload);
  return res.data;
}
