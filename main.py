import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from query_data import query_documents

app = FastAPI(
    title="DocuMind AI API",
    description="RAG API powered by Gemini and Chroma",
    version="1.0.0",
)

# Allow any origin (e.g. Netlify) to call this API from the browser.
# Credentials must be False when using a wildcard origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    chroma_ready = os.path.isdir("chroma")
    return HealthResponse(
        status="ok" if chroma_ready else "degraded",
        message="Connected to Gemini Database"
        if chroma_ready
        else "Chroma database not found — run creating_database.py first",
    )


@app.post("/api/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    x_gemini_api_key: str | None = Header(default=None, alias="X-Gemini-API-Key"),
):
    """Run a RAG query. The client must supply a Gemini API key in X-Gemini-API-Key."""
    if not x_gemini_api_key or not x_gemini_api_key.strip():
        raise HTTPException(
            status_code=401,
            detail="Missing or empty X-Gemini-API-Key header",
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
            detail=f"Failed to process query: {exc}",
        ) from exc


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
