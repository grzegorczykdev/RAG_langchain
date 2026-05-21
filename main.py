from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from query_data import query_documents

app = FastAPI(
    title="DocuMind AI API",
    description="RAG API powered by Gemini and Chroma",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
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
    chroma_ready = __import__("os").path.isdir("chroma")
    return HealthResponse(
        status="ok" if chroma_ready else "degraded",
        message="Connected to Gemini Database"
        if chroma_ready
        else "Chroma database not found — run creating_database.py first",
    )


@app.post("/api/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        result = query_documents(request.question)
        return QueryResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {exc}",
        ) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
