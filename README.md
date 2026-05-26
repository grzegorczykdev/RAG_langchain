# NutriMind AI

[![Vue 3](https://img.shields.io/badge/Vue_3-Composition_API-42b883?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async_API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Chroma](https://img.shields.io/badge/Chroma-Persistent_Vector_DB-FB651E)](https://www.trychroma.com/)
[![Ragas](https://img.shields.io/badge/Ragas-Eval_Pipeline-111827)](https://docs.ragas.io/)
[![Netlify](https://img.shields.io/badge/Deploy-Frontend_Netlify-00C7B7?logo=netlify&logoColor=white)](https://www.netlify.com/)
[![Render](https://img.shields.io/badge/Deploy-Backend_Render-46E3B7)](https://render.com/)
[![Live Demo](https://img.shields.io/badge/Live_Demo-diet--rec.netlify.app-42b883?style=for-the-badge)](https://diet-rec.netlify.app/)

**Local-first RAG for clinical nutrition** — answers grounded in dietitian-curated medical PDFs, with source citations. Polish clinical UI.

**[→ Live demo](https://diet-rec.netlify.app/)** · Frontend on Netlify, API on Render (free tier). First request after idle may take **30–60s** while the backend cold-starts — open **Settings**, add your [Gemini API key](https://aistudio.google.com/), then retry.

---

## Problem → Solution

| | |
|---|---|
| **Problem** | Clinical nutritionists lose hours cross-referencing dense medical textbooks and guideline PDFs; generic LLMs hallucinate dosages, norms, and contraindications with no auditable source trail. |
| **Solution** | A production decoupled RAG stack that retrieves only from a verified PDF corpus (Chroma + semantic search), generates with Gemini under strict grounding prompts, and returns cited source filenames — not open-web knowledge. |

---

## Architecture

Decoupled **SPA + async API**. No monolith; each tier deploys independently.

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser — Vue 3 SPA (Netlify CDN)                              │
│  Settings → localStorage → X-Gemini-API-Key on every query      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS  GET /api/health  POST /api/query
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Render.com — FastAPI + Uvicorn (main.py)                        │
│  CORS-enabled · stateless re: billing keys                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   chroma/ (disk)     query_data.py         Google Gemini
   vector store       LangChain RAG         embed + generate
```

| Tier | Stack | Role |
|------|-------|------|
| **Frontend** | Vue 3 (`<script setup>`, Composition API) · Vite 6 · Tailwind CSS | Clinical query UI, API key settings, citation badges, health status |
| **Backend** | FastAPI · Uvicorn · Pydantic | `GET /api/health`, `POST /api/query`, validation + structured errors |
| **Database** | ChromaDB (`chroma/`, disk-persisted) | Semantic retrieval over ingested PDF chunks |
| **Orchestration** | LangChain | PDF load → chunk → embed → retrieve → prompt → generate |
| **Models** | `gemini-embedding-001` · `gemini-2.5-flash` | Embeddings at index + query time; grounded answer generation |

**RAG guardrails** (`constants.py`): `TOP_K=3`, relevance floor `0.5`, chunks `1000` chars / `500` overlap. Prompt forbids facts outside retrieved context; answers in Polish.

---

## Security & Cost Pattern (BYOK)

No hardcoded Gemini keys in source or production backend config.

```
SettingsModal.vue  →  localStorage (nutrimind_gemini_api_key)
                   →  Header: X-Gemini-API-Key
                   →  FastAPI → query_data.py → Gemini embed + chat
```

| Decision | Why |
|----------|-----|
| User-owned API key | Dietitian controls spend; no shared secret on Render free tier |
| Per-request header | Backend stays stateless; key never committed to repo |
| `401` if header missing | `main.py` rejects anonymous generation |
| `.env` `GEMINI_API_KEY` | CLI (`query_data.py`) and offline eval only — not required for the web BYOK flow |

> Portfolio note: `localStorage` suits demos; production healthcare would use a secrets vault or server-side proxy.

---

## Automated Evaluation Pipeline

Pre-deploy quality gate in `tests/` — **Ragas** + **Hugging Face `datasets`**, with **Gemini as LLM judge**.

| Artifact | Purpose |
|----------|---------|
| `tests/eval_dataset.json` | Curated `question` / `ground_truth` pairs |
| `tests/evaluate_rag.py` | Runs production RAG → scores with Ragas → writes CSV report |
| `tests/evaluation_report.csv` | Per-sample + aggregate metrics (generated on run) |

**Flow**

1. Load ground-truth JSON.
2. For each question, call `query_documents_with_contexts()` (same path as production).
3. Build a Hugging Face `Dataset` with `question`, `answer`, `contexts`, `ground_truth`.
4. Ragas `evaluate()` with metrics: **Faithfulness** (answer grounded in retrieved context) · **Answer Relevancy** (answer addresses the question).
5. Print summary; persist `evaluation_report.csv`.

Requires `GEMINI_API_KEY` in `.env` and an indexed `chroma/` directory.

---

## Tech Stack

| Layer | Technology | Engineering purpose |
|-------|------------|---------------------|
| UI | Vue 3, Vite, Tailwind CSS | Composition API SPA; fast dev/build; clinical UI system |
| API | FastAPI, Uvicorn, Pydantic | Async HTTP, typed contracts, OpenAPI-ready |
| RAG | LangChain Core, LangChain Google GenAI | PDF ingestion, retrieval, prompt orchestration |
| Vectors | ChromaDB, `langchain-chroma` | Persistent on-disk semantic search |
| Ingestion | PyPDFLoader, RecursiveCharacterTextSplitter | Authoritative PDF → chunked documents |
| LLM | Google Gemini 2.5 Flash + embedding-001 | Generation + embeddings (single vendor stack) |
| Quality | Ragas, `datasets`, pandas | Automated faithfulness / relevancy regression |
| Hosting | Netlify (frontend) · Render (API) | Static CDN + containerized Python service |

---

## Repository Layout

```text
rag/
├── .env.example                 # GEMINI_API_KEY (CLI + eval)
├── .gitignore
├── constants.py                 # Paths, chunk sizes, models, TOP_K, threshold
├── creating_database.py         # PDF → chunks → Chroma ingestion
├── query_data.py                # RAG engine (API + CLI + eval hook)
├── main.py                      # FastAPI app, CORS, /api/*
├── requirements.txt
├── data/
│   └── normy_zywienia_dla_populacji_polski.pdf
├── chroma/                      # Generated vector store (gitignored)
├── tests/
│   ├── eval_dataset.json        # Ground-truth Q/A pairs
│   ├── evaluate_rag.py          # Ragas evaluation runner
│   └── evaluation_report.csv    # Generated metrics output
└── frontend/
    ├── netlify.toml             # SPA fallback → index.html
    ├── vite.config.js           # Dev proxy /api → :8000
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── package.json
    ├── index.html
    ├── .env.example             # VITE_API_BASE_URL
    ├── public/
    │   └── favicon.svg
    └── src/
        ├── App.vue
        ├── main.js
        ├── style.css
        ├── config/
        │   └── api.js           # Build-time API base URL resolution
        ├── composables/
        │   ├── useGeminiApiKey.js
        │   ├── useRagQuery.js
        │   └── useTypewriter.js
        ├── components/
        │   ├── AnswerCard.vue
        │   ├── EmptyState.vue
        │   ├── HeaderHero.vue
        │   ├── KnowledgeTopics.vue
        │   ├── LoadingSkeleton.vue
        │   ├── QueryInput.vue
        │   ├── SettingsModal.vue
        │   └── SourcesBadges.vue
        └── utils/
            └── errors.js
```

---

## Quick Start

**Prerequisites:** Python 3.11+, Node.js 18+, [Google AI Studio](https://aistudio.google.com/) API key.

```bash
# Backend deps
pip install -r requirements.txt
cp .env.example .env   # optional: GEMINI_API_KEY for CLI / eval
```

```bash
# 1 — Index PDFs in data/ → chroma/ (requires GEMINI_API_KEY in .env for embeddings)
python creating_database.py
```

```bash
# 2 — API (http://127.0.0.1:8000)
python main.py
```

```bash
# 3 — Frontend (http://localhost:5173)
cd frontend && npm install && npm run dev
```

In the UI: **Settings** → paste Gemini key → ask a question → verify **source badges**.

```bash
# 4 — Offline Ragas eval (requires .env GEMINI_API_KEY + chroma/)
python tests/evaluate_rag.py
```

**CLI (no UI):** `python query_data.py "Twoje pytanie?"` — uses `.env` key.

---

## API Surface

| Method | Path | Notes |
|--------|------|-------|
| `GET` | `/api/health` | `ok` if `chroma/` exists; else `degraded` |
| `POST` | `/api/query` | Body: `{ "question": "..." }` · Header: `X-Gemini-API-Key` · Response: `{ "answer", "sources" }` |

---

## Production Deploy

**Live:** [diet-rec.netlify.app](https://diet-rec.netlify.app/)

| Platform | Setting |
|----------|---------|
| **Render** | Build: `pip install -r requirements.txt && python creating_database.py` · Start: `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Netlify** | Base: `frontend` · Build: `npm run build` · Publish: `dist` · Env: `VITE_API_BASE_URL=https://<render-app>.onrender.com` |

Rebuild frontend after changing `VITE_API_BASE_URL` (inlined at build time).

**Render free tier:** the API sleeps when idle. Expect a cold-start delay on the first health check or query after inactivity; subsequent requests are fast until the next sleep cycle.

---

## Author

**Sylwia Grzegorczyk** — [LinkedIn](https://www.linkedin.com/in/grzegorczyksylwia/)

---

## Disclaimer

Educational / portfolio project. Model output is grounded in indexed documents but **does not replace** licensed dietetic or medical judgment. Verify all recommendations against primary sources.
