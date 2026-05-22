import { ref } from "vue";
import { apiUrl, isApiBaseConfigured } from "../config/api.js";
import { getGeminiApiKey } from "./useGeminiApiKey.js";

function toPolishError(message) {
  if (!message) return "Coś poszło nie tak. Spróbuj ponownie.";
  if (message === "Failed to fetch" || /network/i.test(message)) {
    return "Brak połączenia z serwerem. Sprawdź, czy API jest uruchomione.";
  }
  if (message === "Sprawdzanie stanu nie powiodło się") {
    return "Nie udało się sprawdzić stanu API.";
  }
  return message;
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
    } catch (err) {
      apiStatus.value = "offline";
      statusMessage.value = toPolishError(err.message) || "API niedostępne — uruchom serwer FastAPI";
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
        let message =
          typeof detail === "string"
            ? detail
            : Array.isArray(detail)
              ? detail.map((d) => d.msg || d).join(", ")
              : `Żądanie nie powiodło się (kod ${res.status})`;

        if (res.status === 401) {
          message = "Brak lub nieprawidłowy klucz API Gemini.";
        } else if (res.status === 422) {
          message = "Nieprawidłowe pytanie — wpisz od 1 do 4000 znaków.";
        } else if (res.status >= 500 && !message.startsWith("Nie udało się")) {
          message = `Błąd serwera: ${message}`;
        }

        throw new Error(message);
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
