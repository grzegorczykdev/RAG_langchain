<script setup>
import { onUnmounted, ref, watch } from "vue";
import { Settings, X, Check } from "lucide-vue-next";
import { useGeminiApiKey } from "../composables/useGeminiApiKey.js";

const open = ref(false);
const { apiKey, justSaved, loadFromStorage, save } = useGeminiApiKey();

function close() {
  open.value = false;
}

function onDocumentKeydown(event) {
  if (event.key === "Escape") close();
}

watch(open, (isOpen) => {
  if (isOpen) {
    loadFromStorage();
    document.addEventListener("keydown", onDocumentKeydown);
  } else {
    document.removeEventListener("keydown", onDocumentKeydown);
  }
});

onUnmounted(() => {
  document.removeEventListener("keydown", onDocumentKeydown);
});

function onBackdropClick(event) {
  if (event.target === event.currentTarget) close();
}

function handleSave() {
  save();
}
</script>

<template>
  <div class="fixed right-4 top-4 z-50 sm:right-6 sm:top-6">
    <button
      type="button"
      class="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-300 backdrop-blur-xl transition hover:border-white/20 hover:bg-white/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-accent/40"
      aria-label="Ustawienia"
      @click="open = true"
    >
      <Settings class="h-5 w-5" aria-hidden="true" />
    </button>
  </div>

  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-title"
      @click="onBackdropClick"
    >
      <div
        class="glass-panel w-full max-w-md p-6 shadow-glow animate-fade-in"
        @click.stop
      >
        <div class="mb-5 flex items-start justify-between gap-4">
          <div>
            <h2 id="settings-title" class="font-display text-lg font-semibold text-white">
              Ustawienia
            </h2>
            <p class="mt-1 text-sm text-slate-500">
              Klucz jest zapisywany lokalnie w przeglądarce.
            </p>
          </div>
          <button
            type="button"
            class="rounded-lg p-1.5 text-slate-400 transition hover:bg-white/10 hover:text-white"
            aria-label="Zamknij"
            @click="close"
          >
            <X class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        <label for="gemini-api-key" class="mb-2 block text-sm font-medium text-slate-400">
          Klucz API Gemini
        </label>
        <input
          id="gemini-api-key"
          v-model="apiKey"
          type="password"
          autocomplete="off"
          class="glass-input min-h-0 py-3"
          placeholder="Wklej klucz z Google AI Studio"
          @keydown.enter="handleSave"
        />

        <div class="mt-5 flex items-center justify-end gap-3">
          <p
            v-if="justSaved"
            class="flex items-center gap-1.5 text-sm text-emerald-400"
            role="status"
          >
            <Check class="h-4 w-4" aria-hidden="true" />
            Zapisano
          </p>
          <button type="button" class="btn-glow" @click="handleSave">
            Zapisz
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
