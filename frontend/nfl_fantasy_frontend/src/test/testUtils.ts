/**
 * Shared test utilities and helpers
 * Centralize common test setup and mock patterns
 */

import MockAdapter from 'axios-mock-adapter';
import api from '../api/apiService';
import { API_CONFIG } from '../config/constants';

/**
 * Creates a fresh MockAdapter instance for axios
 * Use in beforeEach to ensure clean state for each test
 */
export function createMockAdapter(): MockAdapter {
  return new MockAdapter(api);
}

/**
 * Builds a full API URL for mocking
 * Ensures consistency between test mocks and production code
 */
export function buildMockUrl(endpoint: string): string {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
}

/**
 * Creates a mock authorization header
 */
export function createAuthHeader(token: string): { Authorization: string } {
  return { Authorization: `Bearer ${token}` };
}

/**
 * Sample test data generators
 */
export const testDataFactory = {
  token: (override?: Partial<string>) => override || 'test-jwt-token',
  
  teamPayload: (override?: Record<string, any>) => ({
    name: 'San Francisco 49ers',
    description: 'NFL Team from California',
    logo_url: 'https://example.com/logo.png',
    league_id: 1,
    ...override,
  }),

  teamResponse: (override?: Record<string, any>) => ({
    id: 10,
    name: 'San Francisco 49ers',
    description: 'NFL Team from California',
    logo_url: 'https://example.com/logo.png',
    league_id: 1,
    created_at: new Date().toISOString(),
    ...override,
  }),

  minimalTeamPayload: (override?: Record<string, any>) => ({
    name: 'Dallas Cowboys',
    league_id: 2,
    ...override,
  }),

  errorResponse: (override?: Record<string, any>) => ({
    detail: 'League not found',
    ...override,
  }),
};
