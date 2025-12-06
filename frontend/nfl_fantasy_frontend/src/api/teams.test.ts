import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import MockAdapter from 'axios-mock-adapter';
import api from './apiService';
import { createTeam, CreateTeamPayload } from './teams';
import {
  createMockAdapter,
  buildMockUrl,
  createAuthHeader,
  testDataFactory,
} from '../test/testUtils';
import { API_ENDPOINTS } from '../config/constants';

describe('Teams API', () => {
  let mock: MockAdapter;
  
  beforeEach(() => {
    mock = createMockAdapter();
  });

  afterEach(() => {
    mock.restore();
  });

  describe('createTeam', () => {
    
    it('should call POST /teams with correct payload and headers', async () => {
      const token = testDataFactory.token();
      const payload = testDataFactory.teamPayload();
      const mockResponse = testDataFactory.teamResponse();

      mock.onPost(buildMockUrl(API_ENDPOINTS.TEAMS.CREATE)).reply(200, mockResponse);

      const result = await createTeam(token, payload);

      expect(result).toEqual(mockResponse);
    });

    it('should work with minimal payload (optional fields omitted)', async () => {
      const token = testDataFactory.token();
      const payload = testDataFactory.minimalTeamPayload();
      const mockResponse = testDataFactory.teamResponse({ name: payload.name });

      mock.onPost(buildMockUrl(API_ENDPOINTS.TEAMS.CREATE)).reply(200, mockResponse);

      const result = await createTeam(token, payload);
      
      expect(result).toEqual(mockResponse);
    });

    it('should handle API errors correctly', async () => {
      const token = testDataFactory.token();
      const payload = testDataFactory.teamPayload({ league_id: 999 });
      const mockError = testDataFactory.errorResponse();

      mock.onPost(buildMockUrl(API_ENDPOINTS.TEAMS.CREATE)).reply(400, mockError);

      await expect(createTeam(token, payload)).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      const token = testDataFactory.token();
      const payload = testDataFactory.minimalTeamPayload();

      mock.onPost(buildMockUrl(API_ENDPOINTS.TEAMS.CREATE)).networkError();

      await expect(createTeam(token, payload)).rejects.toThrow('Network Error');
    });
  });
});
