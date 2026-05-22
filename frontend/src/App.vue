<script setup>
import { onMounted, ref } from "vue";
import HeaderHero from "./components/HeaderHero.vue";
import QueryInput from "./components/QueryInput.vue";
import AnswerCard from "./components/AnswerCard.vue";
import LoadingSkeleton from "./components/LoadingSkeleton.vue";
import EmptyState from "./components/EmptyState.vue";
import SettingsModal from "./components/SettingsModal.vue";
import { useRagQuery } from "./composables/useRagQuery.js";
import { AlertCircle, HeartPulse } from "lucide-vue-next";

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
  <div
    class="relative min-h-screen bg-gradient-to-b from-primary-50/90 via-surface-50 to-accent-50/40"
  >
    <SettingsModal />

    <!-- Dekoracyjne tło — świeże, przestronne -->
    <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div
        class="absolute -left-20 top-16 h-72 w-72 rounded-full bg-primary-200/40 blur-3xl"
      />
      <div
        class="absolute -right-16 top-1/3 h-80 w-80 rounded-full bg-trust-100/60 blur-3xl"
      />
      <div
        class="absolute bottom-0 left-1/2 h-64 w-96 -translate-x-1/2 rounded-full bg-accent-100/50 blur-3xl"
      />
    </div>

    <!-- Górny pasek -->
    <div
      class="relative border-b border-surface-200/80 bg-white/70 px-4 py-3 backdrop-blur-md sm:px-6"
    >
      <div class="mx-auto flex max-w-5xl items-center justify-between">
        <div class="flex items-center gap-2 text-sm font-semibold text-primary-700">
          <HeartPulse class="h-4 w-4" aria-hidden="true" />
          <span>NutriMind AI</span>
        </div>
        <span class="hidden text-xs text-surface-500 sm:inline">
          Asystent oparty na dokumentach naukowych
        </span>
      </div>
    </div>

    <main class="relative mx-auto max-w-4xl space-y-8 px-4 py-8 sm:space-y-10 sm:px-6 sm:py-12 lg:px-8">
      <HeaderHero :status="apiStatus" :status-message="statusMessage" />

      <QueryInput
        :loading="loading"
        :disabled="apiStatus === 'offline'"
        @submit="handleSubmit"
      />

      <div
        v-if="error"
        class="mx-auto flex max-w-3xl items-start gap-3 rounded-card-lg border border-red-200 bg-red-50 px-5 py-4 text-red-800 shadow-soft animate-fade-in"
        role="alert"
      >
        <AlertCircle class="mt-0.5 h-5 w-5 shrink-0 text-red-600" aria-hidden="true" />
        <p class="text-sm leading-relaxed">{{ error }}</p>
      </div>

      <LoadingSkeleton v-if="loading" />

      <AnswerCard
        v-else-if="hasAsked && answer && !error"
        :answer="answer"
        :sources="sources"
      />

      <EmptyState v-else-if="!hasAsked && !loading" />
    </main>

    <footer class="relative border-t border-surface-200/80 bg-white/60 px-4 py-8 backdrop-blur-sm">
      <div class="mx-auto max-w-4xl text-center">
        <p class="text-xs font-medium text-surface-600">
          NutriMind AI · asystent żywienia oparty na sztucznej inteligencji
        </p>
        <p class="mt-1 text-[11px] text-surface-500">
          Informacje mają charakter edukacyjny — nie zastępują konsultacji z dietetykiem
          ani lekarzem.
        </p>
      </div>
    </footer>
  </div>
</template>
