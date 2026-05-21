import { ref } from "vue";

export function useRagQuery() {
  const loading = ref(false);
  const error = ref(null);
  const answer = ref("");
  const sources = ref([]);
  const apiStatus = ref("checking");
  const statusMessage = ref("Checking connection…");

  async function checkHealth() {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) throw new Error("Health check failed");
      const data = await res.json();
      apiStatus.value = data.status === "ok" ? "connected" : "degraded";
      statusMessage.value = data.message;
    } catch {
      apiStatus.value = "offline";
      statusMessage.value = "API offline — start the FastAPI server";
    }
  }

  async function askQuestion(question) {
    loading.value = true;
    error.value = null;
    answer.value = "";
    sources.value = [];

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
              : `Request failed (${res.status})`;
        throw new Error(message);
      }

      answer.value = data.answer ?? "";
      sources.value = Array.isArray(data.sources) ? data.sources : [];
    } catch (err) {
      error.value = err.message || "Something went wrong. Please try again.";
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
