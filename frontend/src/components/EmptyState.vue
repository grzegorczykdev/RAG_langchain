<script setup>
import { Apple, Pill, Scale } from "lucide-vue-next";

const tips = [
  {
    icon: Scale,
    text: "Jakie są zalecane normy spożycia białka dla dorosłych?",
    accent: "primary",
  },
  {
    icon: Apple,
    text: "Podsumuj wytyczne dotyczące warzyw i owoców w diecie",
    accent: "accent",
  },
  {
    icon: Pill,
    text: "Kiedy suplementacja witaminy D jest uzasadniona naukowo?",
    accent: "trust",
  },
];

const accentMap = {
  primary: {
    card: "hover:border-primary-200 hover:bg-primary-50/50",
    icon: "bg-primary-100 text-primary-600",
  },
  accent: {
    card: "hover:border-accent-200 hover:bg-accent-50/50",
    icon: "bg-accent-100 text-accent-600",
  },
  trust: {
    card: "hover:border-trust-200 hover:bg-trust-50/50",
    icon: "bg-trust-100 text-trust-600",
  },
};
</script>

<template>
  <section
    class="mx-auto w-full max-w-3xl animate-fade-in text-center"
    aria-label="Wprowadzenie"
  >
    <h2 class="font-display text-xl font-semibold text-surface-900 sm:text-2xl">
      Rozpocznij konsultację z bazą wiedzy
    </h2>
    <p class="mx-auto mt-2 max-w-lg text-sm leading-relaxed text-surface-600">
      System przeszukuje oficjalne wytyczne żywieniowe i dokumentację suplementacyjną,
      a następnie formułuje odpowiedź wspartą źródłami.
    </p>

    <p class="mt-8 mb-3 text-xs font-semibold uppercase tracking-wider text-surface-500">
      Przykładowe pytania
    </p>

    <div class="grid gap-3 sm:grid-cols-3">
      <div
        v-for="tip in tips"
        :key="tip.text"
        class="health-card health-card-hover flex items-start gap-3 p-4 text-left text-sm text-surface-700 transition-colors"
        :class="accentMap[tip.accent].card"
      >
        <span
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-card"
          :class="accentMap[tip.accent].icon"
        >
          <component :is="tip.icon" class="h-4 w-4" aria-hidden="true" />
        </span>
        <span class="leading-snug">{{ tip.text }}</span>
      </div>
    </div>
  </section>
</template>
