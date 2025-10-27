// frontend/nfl_fantasy_frontend/src/services/leagues.ts
import api from "./apiService";

export type LeagueCreatePayload = {
  name: string;
  description?: string;
  max_teams: 4|6|8|10|12|14|16|18|20;
  password: string;          // 8–12 alphanumeric, at least one lower + one upper
  playoff_format: 4|6;
  allow_decimal_scoring: boolean;
  team_id: number;
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

export type LeagueSearchFilters = {
  name?: string;
  season_id?: number;
  status?: "pre_draft" | "draft" | "in_season" | "completed";
};

export type LeagueSearchResult = {
  id: number;
  uuid?: string;
  name: string;
  description?: string;
  status: string;
  max_teams: number;
  season_id: number;
  season_name: string;
  slots_available: number;
  created_at: string;
};

export type JoinLeagueRequest = {
  password: string;
  user_alias: string;
  team_id: number;
};

export type JoinLeagueResponse = {
  message: string;
  league_id: number;
  team_id: number;
  user_alias: string;
  joined_at: string;
};

export async function searchLeagues(filters?: LeagueSearchFilters) {
  const res = await api.get<LeagueSearchResult[]>("/leagues/search", { params: filters });
  return res.data;
}

export async function joinLeague(leagueId: number, payload: JoinLeagueRequest) {
  const res = await api.post<JoinLeagueResponse>(`/leagues/${leagueId}/join`, payload);
  return res.data;
}
