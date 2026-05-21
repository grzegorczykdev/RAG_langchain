<script setup>
import { Sparkles, Database } from "lucide-vue-next";

defineProps({
  status: {
    type: String,
    default: "checking",
  },
  statusMessage: {
    type: String,
    default: "",
  },
});

const statusStyles = {
  connected: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  degraded: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  offline: "bg-rose-500/20 text-rose-300 border-rose-500/30",
  checking: "bg-slate-500/20 text-slate-400 border-slate-500/30",
};
</script>

<template>
  <header class="text-center animate-fade-in">
    <div
      class="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-glow-sm"
    >
      <Sparkles class="h-7 w-7 text-white" aria-hidden="true" />
    </div>

    <h1 class="font-display text-4xl font-bold tracking-tight text-white sm:text-5xl">
      DocuMind AI
    </h1>
    <p class="mx-auto mt-3 max-w-lg text-base text-slate-400 sm:text-lg">
      Ask questions about your documents. Answers are grounded in your Chroma
      knowledge base powered by Gemini.
    </p>

    <div
      class="mx-auto mt-5 inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm"
      :class="statusStyles[status] || statusStyles.checking"
    >
      <span
        class="h-2 w-2 rounded-full"
        :class="{
          'bg-emerald-400 animate-pulse': status === 'connected',
          'bg-amber-400': status === 'degraded',
          'bg-rose-400': status === 'offline',
          'bg-slate-400 animate-pulse-soft': status === 'checking',
        }"
      />
      <Database class="h-4 w-4 shrink-0 opacity-80" aria-hidden="true" />
      <span>{{ statusMessage }}</span>
    </div>
  </header>
</template>
