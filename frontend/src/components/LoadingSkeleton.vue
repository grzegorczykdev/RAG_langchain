<script setup>
import { Salad } from "lucide-vue-next";
</script>

<template>
  <section
    class="health-card mx-auto w-full max-w-3xl animate-fade-in"
    aria-label="Ładowanie odpowiedzi"
  >
    <div class="mb-4 flex items-center gap-3 border-b border-surface-100 pb-4">
      <div
        class="flex h-10 w-10 items-center justify-center rounded-card bg-primary-100 text-primary-600"
      >
        <Salad class="h-5 w-5 animate-pulse-soft" aria-hidden="true" />
      </div>
      <div class="flex-1 space-y-2">
        <div class="skeleton-line w-36" />
        <div class="skeleton-line w-52 opacity-60" />
      </div>
    </div>

    <div class="space-y-3">
      <div class="skeleton-line w-full" />
      <div class="skeleton-line w-[95%]" />
      <div class="skeleton-line w-[88%]" />
      <div class="skeleton-line w-[70%]" />
    </div>

    <div class="mt-6 flex flex-wrap gap-2">
      <div class="h-7 w-28 rounded-full skeleton-line" />
      <div class="h-7 w-32 rounded-full skeleton-line" />
    </div>
  </section>
</template>
