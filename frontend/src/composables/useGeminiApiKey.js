import { ref } from "vue";

const STORAGE_KEY = "nutrimind_gemini_api_key";
const LEGACY_STORAGE_KEY = "documind_gemini_api_key";
const SAVE_FEEDBACK_MS = 2000;

export function getGeminiApiKey() {
  try {
    const current = localStorage.getItem(STORAGE_KEY);
    if (current) return current;

    const legacy = localStorage.getItem(LEGACY_STORAGE_KEY);
    if (legacy) {
      localStorage.setItem(STORAGE_KEY, legacy);
      localStorage.removeItem(LEGACY_STORAGE_KEY);
      return legacy;
    }

    return "";
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
    }, SAVE_FEEDBACK_MS);
  }

  return { apiKey, justSaved, loadFromStorage, save };
}
