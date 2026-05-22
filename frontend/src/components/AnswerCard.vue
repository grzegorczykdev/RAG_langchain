<script setup>
import { computed, toRef } from "vue";
import { marked } from "marked";
import { Salad } from "lucide-vue-next";
import SourcesBadges from "./SourcesBadges.vue";
import { useTypewriter } from "../composables/useTypewriter.js";

const props = defineProps({
  answer: { type: String, default: "" },
  sources: { type: Array, default: () => [] },
  useTypewriterEffect: { type: Boolean, default: true },
});

const answerRef = toRef(props, "answer");
const { displayText } = useTypewriter(answerRef, {
  speed: 10,
  enabled: props.useTypewriterEffect,
});

const renderedHtml = computed(() => {
  const text = props.useTypewriterEffect ? displayText.value : props.answer;
  return marked.parse(text || "", { breaks: true });
});
</script>

<template>
  <section
    class="health-card mx-auto w-full max-w-3xl animate-fade-in border-primary-100"
    aria-live="polite"
  >
    <div class="mb-5 flex items-center gap-3 border-b border-surface-100 pb-4">
      <div class="icon-badge h-10 w-10 rounded-card">
        <Salad class="h-5 w-5" aria-hidden="true" />
      </div>
      <div>
        <h2 class="font-display text-lg font-semibold text-surface-900">
          Rekomendacja eksperta
        </h2>
        <p class="text-xs text-surface-500">
          Odpowiedź oparta na zatwierdzonych materiałach źródłowych
        </p>
      </div>
    </div>

    <div class="prose-answer min-h-[2rem]" v-html="renderedHtml" />

    <SourcesBadges :sources="sources" />
  </section>
</template>
