<script setup>
import { FileText, BookOpen } from "lucide-vue-next";

defineProps({
  sources: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div v-if="sources.length" class="mt-6 border-t border-surface-100 pt-5 animate-fade-in">
    <div class="mb-3 flex items-center gap-2">
      <BookOpen class="h-4 w-4 text-trust-600" aria-hidden="true" />
      <h3 class="text-xs font-semibold uppercase tracking-wider text-surface-500">
        Źródła i dokumenty
      </h3>
    </div>
    <div class="flex flex-wrap gap-2">
      <span
        v-for="source in sources"
        :key="source"
        class="source-chip"
        :title="source"
      >
        <FileText class="h-3.5 w-3.5 text-primary-600" aria-hidden="true" />
        {{ source }}
      </span>
    </div>
  </div>
</template>
