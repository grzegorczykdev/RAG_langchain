<script setup>
import { onUnmounted, ref, watch } from "vue";
import { Settings, X, Check, KeyRound } from "lucide-vue-next";
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
      class="btn-ghost h-11 w-11 !p-0"
      aria-label="Ustawienia"
      @click="open = true"
    >
      <Settings class="h-5 w-5 text-surface-600" aria-hidden="true" />
    </button>
  </div>

  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-surface-900/40 px-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-title"
      @click="onBackdropClick"
    >
      <div
        class="health-card w-full max-w-md animate-fade-in shadow-card-hover"
        @click.stop
      >
        <div class="mb-5 flex items-start justify-between gap-4">
          <div class="flex items-start gap-3">
            <div class="icon-badge-trust h-10 w-10 shrink-0 rounded-card">
              <KeyRound class="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <h2 id="settings-title" class="font-display text-lg font-semibold text-surface-900">
                Ustawienia
              </h2>
              <p class="mt-1 text-sm text-surface-500">
                Klucz API jest przechowywany wyłącznie w Twojej przeglądarce.
              </p>
            </div>
          </div>
          <button
            type="button"
            class="rounded-card p-1.5 text-surface-400 transition hover:bg-surface-100 hover:text-surface-700"
            aria-label="Zamknij"
            @click="close"
          >
            <X class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        <label for="gemini-api-key" class="mb-2 block text-sm font-medium text-surface-700">
          Klucz API Gemini
        </label>
        <input
          id="gemini-api-key"
          v-model="apiKey"
          type="password"
          autocomplete="off"
          class="health-input-compact"
          placeholder="Wklej klucz z Google AI Studio"
          @keydown.enter="handleSave"
        />

        <div class="mt-5 flex items-center justify-end gap-3">
          <p
            v-if="justSaved"
            class="flex items-center gap-1.5 text-sm font-medium text-primary-700"
            role="status"
          >
            <Check class="h-4 w-4" aria-hidden="true" />
            Zapisano
          </p>
          <button type="button" class="btn-primary" @click="handleSave">
            Zapisz
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
