"""Wspólne stałe konfiguracyjne backendu RAG."""

CHROMA_PATH = "chroma"
DATA_PATH = "data"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 500

RELEVANCE_THRESHOLD = 0.5
TOP_K = 3

GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_CHAT_MODEL = "gemini-2.5-flash"

GEMINI_API_KEY_HEADER = "X-Gemini-API-Key"
