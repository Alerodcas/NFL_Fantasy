import { describe, it, expect, beforeEach } from 'vitest';
import api from './apiService';

describe('API Service', () => {
  
  beforeEach(() => {
    localStorage.clear();
  });

  it('should export an axios instance', () => {
    expect(api).toBeDefined();
    expect(api.post).toBeDefined();
    expect(api.get).toBeDefined();
    expect(api.put).toBeDefined();
    expect(api.delete).toBeDefined();
  });

  it('should have a baseURL configured', () => {
    expect(api.defaults.baseURL).toBeDefined();
    expect(api.defaults.baseURL).toContain('http');
  });
});
