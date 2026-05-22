<script setup>
import { Apple, Pill, ShieldCheck } from "lucide-vue-next";

const topics = [
  {
    icon: Apple,
    label: "Wytyczne żywieniowe",
    description: "Normy i zalecenia dla populacji",
    style: "border-primary-200 bg-primary-50 text-primary-800",
    iconStyle: "bg-primary-100 text-primary-600",
  },
  {
    icon: Pill,
    label: "Suplementacja",
    description: "Dane o preparatach i dawkowaniu",
    style: "border-accent-200 bg-accent-50 text-accent-800",
    iconStyle: "bg-accent-100 text-accent-600",
  },
  {
    icon: ShieldCheck,
    label: "Źródła naukowe",
    description: "Odpowiedzi z cytowanymi dokumentami",
    style: "border-trust-200 bg-trust-50 text-trust-800",
    iconStyle: "bg-trust-100 text-trust-600",
  },
];
</script>

<template>
  <div class="flex flex-wrap items-center justify-center gap-2 sm:gap-3">
    <div
      v-for="topic in topics"
      :key="topic.label"
      class="topic-pill"
      :class="topic.style"
    >
      <span
        class="flex h-6 w-6 items-center justify-center rounded-full"
        :class="topic.iconStyle"
      >
        <component :is="topic.icon" class="h-3.5 w-3.5" aria-hidden="true" />
      </span>
      <span>{{ topic.label }}</span>
    </div>
  </div>
</template>
