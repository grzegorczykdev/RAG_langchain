/** Usuwa końcowy slash z bazowego URL. */
function normalizeBaseUrl(url) {
  return String(url ?? "").trim().replace(/\/$/, "");
}

/**
 * Bazowy URL API:
 * - development (vite / npm run dev): .env* lub http://127.0.0.1:8000
 * - production (vite build): wyłącznie VITE_API_BASE_URL wstrzyknięte przy buildzie
 */
function resolveApiBaseUrl() {
  const fromEnv = import.meta.env.VITE_API_BASE_URL;

  if (import.meta.env.PROD) {
    return normalizeBaseUrl(fromEnv);
  }

  return normalizeBaseUrl(fromEnv) || "http://127.0.0.1:8000";
}

export const API_BASE_URL = resolveApiBaseUrl();

/** W produkcji false, gdy Netlify zbudował aplikację bez VITE_API_BASE_URL. */
export const isApiBaseConfigured = import.meta.env.PROD ? Boolean(API_BASE_URL) : true;

export function apiUrl(path) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalized}`;
}
