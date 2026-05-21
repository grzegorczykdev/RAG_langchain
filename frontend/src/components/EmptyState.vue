<script setup>
import { MessageSquareQuote, BookOpen, Zap } from "lucide-vue-next";

const tips = [
  "Summarize the main plot of the story",
  "Who are the main characters?",
  "What is the conflict in chapter one?",
];
</script>

<template>
  <section
    class="mx-auto w-full max-w-3xl text-center animate-fade-in"
    aria-label="Getting started"
  >
    <div
      class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl glass-panel"
    >
      <MessageSquareQuote class="h-8 w-8 text-accent-glow" aria-hidden="true" />
    </div>

    <h2 class="font-display text-xl font-semibold text-slate-300">
      Ask anything about your documents
    </h2>
    <p class="mx-auto mt-2 max-w-md text-sm text-slate-500">
      DocuMind retrieves relevant passages from your indexed files and answers with
      Gemini using only that context.
    </p>

    <div class="mt-8 grid gap-3 sm:grid-cols-3">
      <div
        v-for="(tip, i) in tips"
        :key="i"
        class="glass-panel flex items-start gap-3 p-4 text-left text-sm text-slate-400"
      >
        <component
          :is="i === 0 ? BookOpen : i === 1 ? MessageSquareQuote : Zap"
          class="mt-0.5 h-4 w-4 shrink-0 text-indigo-400"
          aria-hidden="true"
        />
        <span>{{ tip }}</span>
      </div>
    </div>
  </section>
</template>
