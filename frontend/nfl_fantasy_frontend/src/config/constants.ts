/**
 * Global constants for the application
 * Update these values in ONE place and they will be used everywhere
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  TEAMS: {
    LIST: '/teams',
    CREATE: '/teams',
    GET: (id: string | number) => `/teams/${id}`,
    UPDATE: (id: string | number) => `/teams/${id}`,
    DELETE: (id: string | number) => `/teams/${id}`,
  },
  USERS: {
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    PROFILE: '/users/me',
  },
  LEAGUES: {
    LIST: '/leagues',
    CREATE: '/leagues',
    GET: (id: string | number) => `/leagues/${id}`,
  },
} as const;

// Password Validation
export const PASSWORD_CONFIG = {
  MIN_LENGTH: 8,
  MAX_LENGTH: 12,
  PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z0-9]{8,12}$/,
  RULES: {
    LENGTH: '8-12 caracteres',
    LOWERCASE: 'al menos una letra minúscula',
    UPPERCASE: 'al menos una letra mayúscula',
    DIGIT: 'al menos un número',
    ALPHANUMERIC: 'alfanumérica',
  },
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Error de conexión. Intenta de nuevo.',
  VALIDATION_ERROR: 'Por favor, revisa los datos ingresados.',
  UNAUTHORIZED: 'No tienes permiso para hacer esto.',
  NOT_FOUND: 'El recurso no fue encontrado.',
  SERVER_ERROR: 'Error del servidor. Intenta más tarde.',
  GENERIC_ERROR: 'Algo salió mal. Intenta de nuevo.',
} as const;

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'token',
  USER_ID: 'userId',
  USER_ROLE: 'userRole',
  THEME: 'theme',
} as const;

// UI Configuration
export const UI_CONFIG = {
  TOAST_DURATION: 3000,
  MODAL_ANIMATION_DURATION: 300,
  DEBOUNCE_DELAY: 300,
} as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
} as const;
