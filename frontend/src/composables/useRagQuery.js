import { ref } from "vue";
import { apiUrl, isApiBaseConfigured } from "../config/api.js";
import { getGeminiApiKey } from "./useGeminiApiKey.js";
import { parseApiError, toPolishError } from "../utils/errors.js";

const MSG_MISSING_ENV_BUILD =
  "Brak VITE_API_BASE_URL — ustaw zmienną w Netlify i przebuduj stronę";
const MSG_MISSING_ENV_QUERY =
  "Brak VITE_API_BASE_URL w buildzie produkcyjnym. Ustaw zmienną w Netlify i wykonaj ponowny deploy.";
const MSG_MISSING_API_KEY =
  "Brak klucza API Gemini. Kliknij ikonę ustawień w prawym górnym rogu i zapisz klucz.";
const MSG_API_OFFLINE = "API niedostępne — uruchom serwer FastAPI";

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

export function useRagQuery() {
  const loading = ref(false);
  const error = ref(null);
  const answer = ref("");
  const sources = ref([]);
  const apiStatus = ref("checking");
  const statusMessage = ref("Łączenie z bazą danych…");

  async function checkHealth() {
    if (!isApiBaseConfigured) {
      apiStatus.value = "offline";
      statusMessage.value = MSG_MISSING_ENV_BUILD;
      return;
    }

    try {
      const { res, data } = await fetchJson(apiUrl("/api/health"));
      if (!res.ok) throw new Error("Sprawdzanie stanu nie powiodło się");

      apiStatus.value = data.status === "ok" ? "connected" : "degraded";
      statusMessage.value = data.message;
    } catch (err) {
      apiStatus.value = "offline";
      statusMessage.value = toPolishError(err.message) || MSG_API_OFFLINE;
    }
  }

  async function askQuestion(question) {
    if (!isApiBaseConfigured) {
      error.value = MSG_MISSING_ENV_QUERY;
      return;
    }

    const apiKey = getGeminiApiKey();
    if (!apiKey) {
      error.value = MSG_MISSING_API_KEY;
      return;
    }

    loading.value = true;
    error.value = null;
    answer.value = "";
    sources.value = [];

    try {
      const { res, data } = await fetchJson(apiUrl("/api/query"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Gemini-API-Key": apiKey,
        },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error(parseApiError(data.detail, res.status));
      }

      answer.value = data.answer ?? "";
      sources.value = Array.isArray(data.sources) ? data.sources : [];
    } catch (err) {
      error.value = toPolishError(err.message);
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    answer,
    sources,
    apiStatus,
    statusMessage,
    checkHealth,
    askQuestion,
  };
}
