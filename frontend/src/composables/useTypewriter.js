import { ref, watch, onUnmounted } from "vue";

export function useTypewriter(sourceText, options = {}) {
  const { speed = 12, enabled = true } = options;
  const displayText = ref("");
  let timer = null;

  function clearTimer() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function startTyping(text) {
    clearTimer();
    displayText.value = "";

    if (!enabled || !text) {
      displayText.value = text || "";
      return;
    }

    let index = 0;
    timer = setInterval(() => {
      if (index < text.length) {
        displayText.value += text[index];
        index += 1;
      } else {
        clearTimer();
      }
    }, speed);
  }

  watch(
    () => sourceText.value,
    (text) => startTyping(text ?? ""),
    { immediate: true }
  );

  onUnmounted(clearTimer);

  return { displayText, restart: () => startTyping(sourceText.value ?? "") };
}
