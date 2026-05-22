import os
import sys
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

CHROMA_PATH = "chroma"
RELEVANCE_THRESHOLD = 0.1
TOP_K = 3

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


def _format_source(source: str | None) -> str:
    if not source:
        return "Nieznane źródło"
    return os.path.basename(source)


def query_documents(
    question: str,
    *,
    gemini_api_key: str | None = None,
) -> dict[str, list[str] | str]:
    """Wykonuje zapytanie RAG i zwraca odpowiedź oraz listę plików źródłowych."""
    question = question.strip()
    if not question:
        return {
            "answer": "Podaj pytanie, aby uzyskać odpowiedź.",
            "sources": [],
        }

    api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "answer": "Brak klucza API Gemini. Ustaw klucz w ustawieniach aplikacji.",
            "sources": [],
        }

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=api_key,
    )
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    results = db.similarity_search_with_relevance_scores(question, k=TOP_K)

    if len(results) == 0 or results[0][1] < RELEVANCE_THRESHOLD:
        return {
            "answer": (
                "Nie znaleziono w dokumentach informacji pasujących do Twojego pytania. "
                "Spróbuj sformułować je inaczej lub sprawdź, czy baza wiedzy została zindeksowana."
            ),
            "sources": [],
        }

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=question)

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
    )
    response = model.invoke(prompt)
    response_text = response.content if hasattr(response, "content") else str(response)

    sources = sorted(
        {_format_source(doc.metadata.get("source")) for doc, _score in results}
    )

    return {
        "answer": response_text,
        "sources": sources,
    }


def main():
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
