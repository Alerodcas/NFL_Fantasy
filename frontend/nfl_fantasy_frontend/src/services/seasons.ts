import api from "./apiService"; // your existing Axios instance

export interface SeasonCreatePayload {
  name: string;
  year: number;
  start_date: string;
  end_date: string;
  description?: string;
}

export interface SeasonCreatedResponse {
  id: number;
  name: string;
  year: number;
  start_date: string;
  end_date: string;
  description?: string;
}

export async function createSeason(payload: SeasonCreatePayload): Promise<SeasonCreatedResponse> {
  const { data } = await api.post("/seasons", payload);
  return data;
}
