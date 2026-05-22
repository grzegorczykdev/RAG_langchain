<script setup>
import { computed, toRef } from "vue";
import { marked } from "marked";
import { Bot } from "lucide-vue-next";
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
    class="glass-panel mx-auto w-full max-w-3xl p-6 shadow-glow animate-fade-in"
    aria-live="polite"
  >
    <div class="mb-4 flex items-center gap-3">
      <div
        class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/30 to-violet-600/30 text-accent-glow"
      >
        <Bot class="h-5 w-5" aria-hidden="true" />
      </div>
      <div>
        <h2 class="font-display text-lg font-semibold text-white">Odpowiedź AI</h2>
        <p class="text-xs text-slate-500">Wygenerowana na podstawie Twoich dokumentów</p>
      </div>
    </div>

    <div
      class="prose-answer min-h-[2rem]"
      v-html="renderedHtml"
    />

    <SourcesBadges :sources="sources" />
  </section>
</template>
