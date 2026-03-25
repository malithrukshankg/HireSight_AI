/**
 * Single source for the API Gateway base URL.
 * Set VITE_API_URL in .env (see .env.example).
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000"; ///api
