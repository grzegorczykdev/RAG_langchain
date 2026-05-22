<script setup>
import { computed } from "vue";
import { Leaf, Database } from "lucide-vue-next";
import KnowledgeTopics from "./KnowledgeTopics.vue";

const props = defineProps({
  status: {
    type: String,
    default: "checking",
  },
  statusMessage: {
    type: String,
    default: "",
  },
});

const STATUS_CONFIG = {
  connected: {
    badge: "border-primary-200 bg-primary-50 text-primary-800",
    dot: "bg-primary-500 animate-pulse",
  },
  degraded: {
    badge: "border-accent-200 bg-accent-50 text-accent-800",
    dot: "bg-accent-500",
  },
  offline: {
    badge: "border-red-200 bg-red-50 text-red-800",
    dot: "bg-red-500",
  },
  checking: {
    badge: "border-surface-200 bg-white text-surface-600",
    dot: "bg-surface-300 animate-pulse-soft",
  },
};

const activeStatus = computed(
  () => STATUS_CONFIG[props.status] ?? STATUS_CONFIG.checking,
);
</script>

<template>
  <header class="animate-fade-in text-center">
    <div class="icon-badge mx-auto mb-5 h-14 w-14 rounded-card-lg">
      <Leaf class="h-7 w-7" aria-hidden="true" />
    </div>

    <p class="mb-2 text-xs font-semibold uppercase tracking-widest text-primary-600">
      Dietetyka · Żywienie · Suplementacja
    </p>

    <h1 class="font-display text-3xl font-bold tracking-tight text-surface-900 sm:text-4xl lg:text-5xl">
      NutriMind
      <span class="text-primary-600">AI</span>
    </h1>

    <p class="mx-auto mt-3 max-w-xl text-base leading-relaxed text-surface-600 sm:text-lg">
      Zadawaj pytania o oficjalne wytyczne żywieniowe i dane suplementacyjne.
      Odpowiedzi powstają wyłącznie na podstawie zindeksowanych dokumentów.
    </p>

    <div class="mt-6">
      <KnowledgeTopics />
    </div>

    <div
      class="mx-auto mt-6 inline-flex max-w-full items-center gap-2 rounded-full border px-4 py-2 text-sm shadow-soft"
      :class="activeStatus.badge"
    >
      <span class="h-2 w-2 shrink-0 rounded-full" :class="activeStatus.dot" />
      <Database class="h-4 w-4 shrink-0 opacity-70" aria-hidden="true" />
      <span class="truncate">{{ statusMessage }}</span>
    </div>
  </header>
</template>
