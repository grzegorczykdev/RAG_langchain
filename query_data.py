import os
import sys
from typing import TypedDict

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from constants import (
    CHROMA_PATH,
    GEMINI_CHAT_MODEL,
    GEMINI_EMBEDDING_MODEL,
    RELEVANCE_THRESHOLD,
    TOP_K,
)

load_dotenv()

PROMPT_TEMPLATE = """
Jesteś asystentem dietetycznym. Odpowiedz na pytanie WYŁĄCZNIE na podstawie poniższego kontekstu
z oficjalnych dokumentów (wytyczne żywieniowe, suplementacja).

Zasady:
- Odpowiadaj zawsze po polsku.
- Używaj jasnego, profesjonalnego języka zrozumiałego dla użytkownika.
- Jeśli kontekst nie zawiera odpowiedzi, napisz, że w dostępnych materiałach brak takich informacji.
- Nie wymyślaj faktów spoza kontekstu.

Kontekst:
{context}

---

Pytanie: {question}
"""

CHAT_PROMPT = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

MSG_EMPTY_QUESTION = "Podaj pytanie, aby uzyskać odpowiedź."
MSG_MISSING_API_KEY = "Brak klucza API Gemini. Ustaw klucz w ustawieniach aplikacji."
MSG_NO_MATCH = (
    "Nie znaleziono w dokumentach informacji pasujących do Twojego pytania. "
    "Spróbuj sformułować je inaczej lub sprawdź, czy baza wiedzy została zindeksowana."
)


class QueryResult(TypedDict):
    answer: str
    sources: list[str]


def _result(answer: str, sources: list[str] | None = None) -> QueryResult:
    return {"answer": answer, "sources": sources or []}


def _format_source(source: str | None) -> str:
    if not source:
        return "Nieznane źródło"
    return os.path.basename(source)


def _resolve_api_key(gemini_api_key: str | None) -> str | None:
    key = (gemini_api_key or os.environ.get("GEMINI_API_KEY") or "").strip()
    return key or None


def _extract_content(response: object) -> str:
    content = getattr(response, "content", None)
    return content if isinstance(content, str) else str(response)


def query_documents(
    question: str,
    *,
    gemini_api_key: str | None = None,
) -> QueryResult:
    """Wykonuje zapytanie RAG i zwraca odpowiedź oraz listę plików źródłowych."""
    question = question.strip()
    if not question:
        return _result(MSG_EMPTY_QUESTION)

    api_key = _resolve_api_key(gemini_api_key)
    if not api_key:
        return _result(MSG_MISSING_API_KEY)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=GEMINI_EMBEDDING_MODEL,
        google_api_key=api_key,
    )
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    results = db.similarity_search_with_relevance_scores(question, k=TOP_K)

    if not results or results[0][1] < RELEVANCE_THRESHOLD:
        return _result(MSG_NO_MATCH)

    context_text = "\n\n---\n\n".join(doc.page_content for doc, _ in results)
    prompt = CHAT_PROMPT.format(context=context_text, question=question)

    model = ChatGoogleGenerativeAI(
        model=GEMINI_CHAT_MODEL,
        google_api_key=api_key,
    )
    response_text = _extract_content(model.invoke(prompt))

    sources = sorted({_format_source(doc.metadata.get("source")) for doc, _ in results})

    return _result(response_text, sources)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Błąd: podaj pytanie jako argument. "
            'Przykład: python query_data.py "Jakie są normy białka?"'
        )
        return

    result = query_documents(sys.argv[1])

    print("\n=== ODPOWIEDŹ AI ===")
    print(result["answer"])
    print("\n=== ŹRÓDŁA ===")
    if result["sources"]:
        print(f"Informacje znalezione w: {', '.join(result['sources'])}\n")
    else:
        print("Brak dopasowanych źródeł.\n")


if __name__ == "__main__":
    main()
