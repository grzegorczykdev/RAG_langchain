import os

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from query_data import query_documents

app = FastAPI(
    title="NutriMind AI — API",
    description="API RAG do wytycznych żywieniowych i suplementacji (Gemini + Chroma)",
    version="1.0.0",
)

# Zezwól na żądania z dowolnej domeny (np. Netlify).
# Przy origin "*" credentials musi być False.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Pytanie użytkownika dotyczące żywienia lub suplementacji",
    )


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


class HealthResponse(BaseModel):
    status: str
    message: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, _exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": (
                "Nieprawidłowe żądanie. Pole „question” jest wymagane "
                "(od 1 do 4000 znaków)."
            )
        },
    )


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    chroma_ready = os.path.isdir("chroma")
    return HealthResponse(
        status="ok" if chroma_ready else "degraded",
        message=(
            "Połączono z bazą wiedzy Chroma"
            if chroma_ready
            else "Baza Chroma nie istnieje — uruchom najpierw creating_database.py"
        ),
    )


@app.post("/api/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    x_gemini_api_key: str | None = Header(default=None, alias="X-Gemini-API-Key"),
):
    """Zapytanie RAG — klient musi przesłać klucz Gemini w nagłówku X-Gemini-API-Key."""
    if not x_gemini_api_key or not x_gemini_api_key.strip():
        raise HTTPException(
            status_code=401,
            detail="Brak nagłówka X-Gemini-API-Key lub jest pusty",
        )

    try:
        result = query_documents(
            request.question,
            gemini_api_key=x_gemini_api_key.strip(),
        )
        return QueryResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Nie udało się przetworzyć zapytania: {exc}",
        ) from exc


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
