function normalizeBaseUrl(url) {
  return String(url ?? "").trim().replace(/\/$/, "");
}

function resolveApiBaseUrl() {
  const fromEnv = import.meta.env.VITE_API_BASE_URL;

  if (import.meta.env.PROD) {
    return normalizeBaseUrl(fromEnv);
  }

  return normalizeBaseUrl(fromEnv) || "http://127.0.0.1:8000";
}

const API_BASE_URL = resolveApiBaseUrl();

export const isApiBaseConfigured = import.meta.env.PROD
  ? Boolean(API_BASE_URL)
  : true;

export function apiUrl(path) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalized}`;
}
