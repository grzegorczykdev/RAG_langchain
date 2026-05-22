import { ref } from "vue";

const STORAGE_KEY = "documind_gemini_api_key";

export function getGeminiApiKey() {
  try {
    return localStorage.getItem(STORAGE_KEY) || "";
  } catch {
    return "";
  }
}

export function setGeminiApiKey(key) {
  const trimmed = (key || "").trim();
  localStorage.setItem(STORAGE_KEY, trimmed);
  return trimmed;
}

export function useGeminiApiKey() {
  const apiKey = ref(getGeminiApiKey());
  const justSaved = ref(false);

  function loadFromStorage() {
    apiKey.value = getGeminiApiKey();
  }

  function save() {
    setGeminiApiKey(apiKey.value);
    apiKey.value = getGeminiApiKey();
    justSaved.value = true;
    window.setTimeout(() => {
      justSaved.value = false;
    }, 2000);
  }

  return { apiKey, justSaved, loadFromStorage, save };
}
