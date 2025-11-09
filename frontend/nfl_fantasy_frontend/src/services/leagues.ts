// frontend/nfl_fantasy_frontend/src/services/leagues.ts
import api from "./apiService";

export type LeagueCreatePayload = {
  name: string;
  description?: string;
  max_teams: 4|6|8|10|12|14|16|18|20;
  password: string;          // 8–12 alphanumeric, at least one lower + one upper
  playoff_format: 4|6;
  allow_decimal_scoring: boolean;
<<<<<<< HEAD
  fantasy_team: {
    name: string;
    image_url?: string;
  };
=======
  team_id: number;
>>>>>>> main
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
<<<<<<< HEAD
  fantasy_team: {
    name: string;
    image_url?: string;
  };
=======
  team_id: number;
>>>>>>> main
};

export type JoinLeagueResponse = {
  message: string;
  league_id: number;
  team_id: number;
  user_alias: string;
  joined_at: string;
};

<<<<<<< HEAD
/**
 * Search leagues by filters. To prevent accidental enumeration, this function
 * requires at least one filter. If no filters are provided, it returns an empty array
 * without calling the API.
 */
export async function searchLeagues(filters?: LeagueSearchFilters) {
  // Frontend guard: don't call the API without a concrete filter
  if (!filters || (!filters.name && !filters.season_id && !filters.status)) {
    return [];
  }

  // If using name, enforce a minimal length to reduce broad scans
  if (filters.name && filters.name.trim().length < 3) {
    return [];
  }

=======
export async function searchLeagues(filters?: LeagueSearchFilters) {
>>>>>>> main
  const res = await api.get<LeagueSearchResult[]>("/leagues/search", { params: filters });
  return res.data;
}

<<<<<<< HEAD
/** Convenience helper when searching by name only. */
export async function searchLeaguesByName(name: string) {
  const trimmed = name.trim();
  if (trimmed.length < 3) return [];
  return searchLeagues({ name: trimmed });
}

=======
>>>>>>> main
export async function joinLeague(leagueId: number, payload: JoinLeagueRequest) {
  const res = await api.post<JoinLeagueResponse>(`/leagues/${leagueId}/join`, payload);
  return res.data;
}
<<<<<<< HEAD

export type UploadFantasyTeamImageResponse = {
  image_url: string;
  thumbnail_url: string;
};

export async function uploadFantasyTeamImage(file: File) {
  const form = new FormData();
  form.append('image', file);
  const res = await api.post<UploadFantasyTeamImageResponse>("/leagues/fantasy-team/upload", form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
}
=======
>>>>>>> main
