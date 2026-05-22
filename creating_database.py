import os
import shutil

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import (
    CHROMA_PATH,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_PATH,
    GEMINI_EMBEDDING_MODEL,
)

load_dotenv()


def main() -> None:
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    print("Wczytywanie dokumentów PDF...")
    loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()

    print("Dzielenie tekstów na mniejsze fragmenty...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    print(f"Zapisywanie {len(chunks)} fragmentów do bazy danych Chroma...")
    embeddings = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
    Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)

    print("Baza danych gotowa i zapisana na dysku!")


if __name__ == "__main__":
    main()
