import axios from 'axios';
import { API_BASE } from '../config/server';

const api = axios.create({
  baseURL: API_BASE,
});

// Interceptor para agregar el token JWT a cada solicitud
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to normalize server-provided error details so components
// can display `error.response.data.detail` reliably. We attach `serverDetail`
// to the error object when present.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    try {
      const detail = error?.response?.data?.detail ?? error?.response?.data?.message ?? null;
      if (detail) {
        error.serverDetail = detail;
      }
    } catch (e) {
      // swallow any parsing error and keep rejecting the original error
    }
    return Promise.reject(error);
  }
);

export default api;