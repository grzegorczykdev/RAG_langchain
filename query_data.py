import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

CHROMA_PATH = "chroma"
RELEVANCE_THRESHOLD = 0.5
TOP_K = 3

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Question: {question}
"""


def _format_source(source: str | None) -> str:
    if not source:
        return "Unknown"
    return os.path.basename(source)


def query_documents(question: str) -> dict[str, list[str] | str]:
    """Run RAG query and return answer with source filenames."""
    question = question.strip()
    if not question:
        return {
            "answer": "Please provide a question.",
            "sources": [],
        }

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    results = db.similarity_search_with_relevance_scores(question, k=TOP_K)

    if len(results) == 0 or results[0][1] < RELEVANCE_THRESHOLD:
        return {
            "answer": "Could not find matching information in your documents.",
            "sources": [],
        }

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=question)

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
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
            "Error: You must provide a question. Example: python query_data.py 'Your question here'"
        )
        return

    result = query_documents(sys.argv[1])

    print("\n=== AI RESPONSE ===")
    print(result["answer"])
    print("\n=== SOURCES ===")
    if result["sources"]:
        print(f"Information found in: {', '.join(result['sources'])}\n")
    else:
        print("No sources found.\n")


if __name__ == "__main__":
    main()
