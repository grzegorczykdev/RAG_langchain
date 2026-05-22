import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 1. Wczytujemy klucz API z pliku .env
load_dotenv()

CHROMA_PATH = "chroma"
DATA_PATH = "data"


def main():
    # Jeśli stara baza danych istnieje, usuwamy ją, żeby stworzyć nową i świeżą
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # 2. Wczytujemy wszystkie pliki tekstowe z folderu 'data'
    print("Wczytywanie dokumentów PDF...")
    loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()

    # 3. Tniemy tekst na mniejsze kawałki (tzw. chunki)
    # Każdy kawałek ma max 1000 znaków i nachodzi na kolejny o 500 znaków
    print("Dzielenie tekstów na mniejsze fragmenty...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
    chunks = text_splitter.split_documents(documents)

    # 4. Tworzymy bazę wektorową Chroma przy użyciu modeli Gemini
    print(f"Zapisywanie {len(chunks)} fragmentów do bazy danych Chroma...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    # Ta linijka automatycznie tworzy bazę i zapisuje ją w nowym folderze 'chroma'
    Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
    print("Baza danych gotowa i zapisana na dysku!")


if __name__ == "__main__":
    main()
