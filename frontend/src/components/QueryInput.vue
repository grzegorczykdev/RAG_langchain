<script setup>
import { ref } from "vue";
import { Send, Loader2 } from "lucide-vue-next";

defineProps({
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(["submit"]);

const question = ref("");

function handleSubmit() {
  const trimmed = question.value.trim();
  if (!trimmed) return;
  emit("submit", trimmed);
}

function onKeydown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSubmit();
  }
}
</script>

<template>
  <section class="glass-panel mx-auto w-full max-w-3xl p-6 shadow-glow-sm animate-fade-in">
    <label for="question" class="mb-3 block text-sm font-medium text-slate-400">
      Twoje pytanie
    </label>
    <textarea
      id="question"
      v-model="question"
      rows="3"
      class="glass-input min-h-[120px]"
      placeholder="np. Co dzieje się, gdy Dorota spotyka Czarnoksiężnika?"
      :disabled="loading || disabled"
      @keydown="onKeydown"
    />

    <div class="mt-4 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
      <p class="text-xs text-slate-500">
        <kbd class="rounded bg-surface-800 px-1.5 py-0.5">Enter</kbd> — wyślij,
        <kbd class="rounded bg-surface-800 px-1.5 py-0.5">Shift+Enter</kbd> — nowa linia
      </p>

      <button
        type="button"
        class="btn-glow shrink-0"
        :disabled="loading || disabled || !question.trim()"
        @click="handleSubmit"
      >
        <Loader2 v-if="loading" class="h-5 w-5 animate-spin" aria-hidden="true" />
        <Send v-else class="h-5 w-5" aria-hidden="true" />
        {{ loading ? "Myślę…" : "Zapytaj AI" }}
      </button>
    </div>
  </section>
</template>
