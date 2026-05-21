import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 1. Load the Google API key from the .env file
load_dotenv()

CHROMA_PATH = "chroma"

# The template message for the AI model
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Question: {question}
"""


def main():
    # Check if the user provided a question in the terminal
    if len(sys.argv) < 2:
        print(
            "Error: You must provide a question. Example: python query_data.py 'Your question here'"
        )
        return

    query_text = sys.argv[1]

    # 2. Load the existing database from your disk using Gemini Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # 3. Search the database for the top 3 most relevant text chunks
    results = db.similarity_search_with_relevance_scores(query_text, k=3)

    print(results)

    # If no matching pieces are found or the relevance score is too low, stop
    if len(results) == 0 or results[0][1] < 0.5:
        print("Could not find matching information in your documents.")
        return

    # Combine the contents of the found chunks into a single text block (context)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # 4. Prepare the final prompt by injecting the context and the user's question
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # 5. Send the prompt to the Gemini text model (gemini-2.5-flash is fast and free)
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    # Generate the response using invoke
    response = model.invoke(prompt)
    response_text = response.content

    # 6. Extract the source filenames from the metadata
    sources = [doc.metadata.get("source", "Unknown") for doc, _score in results]

    # Print the final result in the terminal
    print("\n=== AI RESPONSE ===")
    print(response_text)
    print("\n=== SOURCES ===")
    print(f"Information found in: {', '.join(set(sources))}\n")


if __name__ == "__main__":
    main()
