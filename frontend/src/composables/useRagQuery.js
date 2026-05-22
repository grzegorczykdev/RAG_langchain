import { ref } from "vue";
import { apiUrl, isApiBaseConfigured } from "../config/api.js";
import { getGeminiApiKey } from "./useGeminiApiKey.js";

export function useRagQuery() {
  const loading = ref(false);
  const error = ref(null);
  const answer = ref("");
  const sources = ref([]);
  const apiStatus = ref("checking");
  const statusMessage = ref("Sprawdzanie połączenia…");

  async function checkHealth() {
    if (!isApiBaseConfigured) {
      apiStatus.value = "offline";
      statusMessage.value =
        "Brak VITE_API_BASE_URL — ustaw zmienną w Netlify i przebuduj stronę";
      return;
    }

    try {
      const res = await fetch(apiUrl("/api/health"));
      if (!res.ok) throw new Error("Sprawdzanie stanu nie powiodło się");
      const data = await res.json();
      apiStatus.value = data.status === "ok" ? "connected" : "degraded";
      statusMessage.value = data.message;
    } catch {
      apiStatus.value = "offline";
      statusMessage.value = "API niedostępne — uruchom serwer FastAPI";
    }
  }

  async function askQuestion(question) {
    if (!isApiBaseConfigured) {
      error.value =
        "Brak VITE_API_BASE_URL w buildzie produkcyjnym. Ustaw zmienną w Netlify i wykonaj ponowny deploy.";
      return;
    }

    const apiKey = getGeminiApiKey();
    if (!apiKey) {
      error.value =
        "Brak klucza API Gemini. Kliknij ikonę ustawień w prawym górnym rogu i zapisz klucz.";
      return;
    }

    loading.value = true;
    error.value = null;
    answer.value = "";
    sources.value = [];

    try {
      const res = await fetch(apiUrl("/api/query"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Gemini-API-Key": apiKey,
        },
        body: JSON.stringify({ question }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const detail = data.detail;
        const message =
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((d) => d.msg || d).join(", ")
              : `Żądanie nie powiodło się (${res.status})`;
        throw new Error(message);
      }

      answer.value = data.answer ?? "";
      sources.value = Array.isArray(data.sources) ? data.sources : [];
    } catch (err) {
      error.value =
        err.message || "Coś poszło nie tak. Spróbuj ponownie.";
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
