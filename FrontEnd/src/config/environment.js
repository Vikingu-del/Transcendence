const env = import.meta.env;

export const config = {
  API_BASE_URL: env.VITE_API_BASE_URL || 'https://localhost',
  WS_BASE_URL: env.VITE_WS_BASE_URL || 'wss://localhost',
  AUTH_PORT: env.VITE_AUTH_PORT || '8001',
  USER_PORT: env.VITE_USER_PORT || '8000',
  GAME_PORT: env.VITE_GAME_PORT || '8005'
};