const DEFAULT_ERROR = "Coś poszło nie tak. Spróbuj ponownie.";

const STATUS_MESSAGES = {
  401: "Brak lub nieprawidłowy klucz API Gemini.",
  422: "Nieprawidłowe pytanie — wpisz od 1 do 4000 znaków.",
};

export function toPolishError(message) {
  if (!message) return DEFAULT_ERROR;
  if (message === "Failed to fetch" || /network/i.test(message)) {
    return "Brak połączenia z serwerem. Sprawdź, czy API jest uruchomione.";
  }
  if (message === "Sprawdzanie stanu nie powiodło się") {
    return "Nie udało się sprawdzić stanu API.";
  }
  return message;
}

function formatDetail(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || item).join(", ");
  }
  return null;
}

export function parseApiError(detail, status) {
  const known = STATUS_MESSAGES[status];
  if (known) return known;

  let message = formatDetail(detail) ?? `Żądanie nie powiodło się (kod ${status})`;

  if (status >= 500 && !message.startsWith("Nie udało się")) {
    message = `Błąd serwera: ${message}`;
  }

  return message;
}
