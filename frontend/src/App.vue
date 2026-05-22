<script setup>
import { onMounted, ref } from "vue";
import HeaderHero from "./components/HeaderHero.vue";
import QueryInput from "./components/QueryInput.vue";
import AnswerCard from "./components/AnswerCard.vue";
import LoadingSkeleton from "./components/LoadingSkeleton.vue";
import EmptyState from "./components/EmptyState.vue";
import SettingsModal from "./components/SettingsModal.vue";
import { useRagQuery } from "./composables/useRagQuery.js";
import { AlertCircle } from "lucide-vue-next";

const hasAsked = ref(false);

const {
  loading,
  error,
  answer,
  sources,
  apiStatus,
  statusMessage,
  checkHealth,
  askQuestion,
} = useRagQuery();

onMounted(() => {
  checkHealth();
});

async function handleSubmit(question) {
  hasAsked.value = true;
  await askQuestion(question);
}
</script>

<template>
  <div class="relative min-h-screen px-4 py-10 sm:px-6 lg:px-8">
    <SettingsModal />
    <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div
        class="absolute -left-32 top-20 h-64 w-64 rounded-full bg-indigo-600/10 blur-3xl"
      />
      <div
        class="absolute -right-24 bottom-32 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl"
      />
    </div>

    <main class="relative mx-auto max-w-4xl space-y-10">
      <HeaderHero :status="apiStatus" :status-message="statusMessage" />

      <QueryInput
        :loading="loading"
        :disabled="apiStatus === 'offline'"
        @submit="handleSubmit"
      />

      <div
        v-if="error"
        class="mx-auto flex max-w-3xl items-start gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 px-5 py-4 text-rose-200 animate-fade-in"
        role="alert"
      >
        <AlertCircle class="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
        <p class="text-sm">{{ error }}</p>
      </div>

      <LoadingSkeleton v-if="loading" />

      <AnswerCard
        v-else-if="hasAsked && answer && !error"
        :answer="answer"
        :sources="sources"
      />

      <EmptyState v-else-if="!hasAsked && !loading" />
    </main>

    <footer class="relative mt-16 text-center text-xs text-slate-600">
      DocuMind AI · Vue 3 + FastAPI + Gemini RAG
    </footer>
  </div>
</template>
