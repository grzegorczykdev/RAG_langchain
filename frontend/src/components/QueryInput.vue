<script setup>
import { ref } from "vue";
import { MessageCircle } from "lucide-vue-next";

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
  <section class="health-card health-card-hover mx-auto w-full max-w-3xl animate-fade-in">
    <div class="mb-4 flex items-center gap-3">
      <div class="icon-badge-trust h-10 w-10 rounded-card">
        <MessageCircle class="h-5 w-5" aria-hidden="true" />
      </div>
      <div>
        <label for="question" class="block font-display text-base font-semibold text-surface-900">
          Twoje pytanie
        </label>
        <p class="text-xs text-surface-500">Zapytaj o normy, produkty lub suplementację</p>
      </div>
    </div>

    <textarea
      id="question"
      v-model="question"
      rows="3"
      class="health-input min-h-[120px]"
      placeholder="np. Jakie są zalecane dzienne normy białka według wytycznych żywieniowych?"
      :disabled="loading || disabled"
      @keydown="onKeydown"
    />

    <div
      class="mt-4 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <p class="text-xs text-surface-500">
        <kbd class="kbd-hint">Enter</kbd> — wyślij,
        <kbd class="kbd-hint">Shift+Enter</kbd> — nowa linia
      </p>

      <button
        type="button"
        class="btn-primary shrink-0"
        :disabled="loading || disabled || !question.trim()"
        @click="handleSubmit"
      >
        {{ loading ? "Analizuję…" : "Zapytaj eksperta" }}
      </button>
    </div>
  </section>
</template>
