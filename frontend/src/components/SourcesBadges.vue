<script setup>
import { FileText } from "lucide-vue-next";

defineProps({
  sources: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div v-if="sources.length" class="mt-6 border-t border-white/10 pt-5 animate-fade-in">
    <h3 class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
      Sources
    </h3>
    <div class="flex flex-wrap gap-2">
      <span
        v-for="source in sources"
        :key="source"
        class="source-chip"
        :title="source"
      >
        <FileText class="h-3.5 w-3.5 text-accent-glow" aria-hidden="true" />
        {{ source }}
      </span>
    </div>
  </div>
</template>
