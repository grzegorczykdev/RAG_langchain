# NutriMind AI — Full-Stack Production RAG Platform

[![Vue 3](https://img.shields.io/badge/Vue-3.5-42b883?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Chroma](https://img.shields.io/badge/Chroma-Vector%20DB-orange)](https://www.trychroma.com/)
[![Netlify](https://img.shields.io/badge/Frontend-Netlify-00C7B7?logo=netlify&logoColor=white)](https://www.netlify.com/)
[![Render](https://img.shields.io/badge/Backend-Render-46E3B7)](https://render.com/)

> **A closed-loop, citation-backed AI assistant for clinical nutritionists** — grounded exclusively in dietitian-curated medical PDFs, not the open internet.

---

## Table of Contents

- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Data Pipeline & Ingestion](#data-pipeline--ingestion)
- [Core RAG Runtime](#core-rag-runtime)
- [Architecture & Cloud Deployment](#architecture--cloud-deployment)
- [API Key Management (Security Pattern)](#api-key-management-security-pattern)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites & Quick Start](#prerequisites--quick-start)
- [API Reference](#api-reference)
- [Production Deployment](#production-deployment)
- [What I Learned & Engineering Takeaways](#what-i-learned--engineering-takeaways)

---

## The Problem

Clinical nutritionists and dietitians routinely spend **hours manually searching** thick reference textbooks, national dietary guidelines, and medical PDFs to find trustworthy nutritional data for patient care.

General-purpose LLMs (ChatGPT, vanilla Gemini, etc.) are a poor fit for this workflow because they:

| Limitation | Impact on clinical work |
| :--- | :--- |
| **Hallucination** | Invented dosages, norms, or contraindications |
| **No domain grounding** | Answers blend unverified web content with medical fact |
| **No source attribution** | Impossible to audit or defend a recommendation |
| **No private corpus** | Cannot anchor answers to *your* institution’s approved documents |

Dietitians need answers that are **traceable, conservative, and limited to a verified knowledge base they control**.

---

## The Solution

**NutriMind AI** implements **Retrieval-Augmented Generation (RAG)** as a production full-stack application:

1. **Ingest** authoritative PDFs (e.g. national nutrition guidelines, supplementation references) into a local vector database.
2. **Retrieve** only the most relevant chunks for each user question via semantic search.
3. **Generate** answers with **Gemini 2.5 Flash**, constrained by a strict prompt that forbids extrapolation beyond retrieved context.
4. **Return cited source filenames** so the dietitian can verify every claim.

The result is a **closed-loop, trusted assistant** — not a general chatbot — anchored to a single corpus chosen and trusted by the practitioner.

---

## Data Pipeline & Ingestion

Ingestion is handled by `creating_database.py` and configured via shared constants in `constants.py`.

```
data/*.pdf  →  PyPDFLoader  →  Chunking  →  Embeddings  →  chroma/ (persistent)
```

### Step 1 — Ingestion (PDF parsing)

- **Loader:** LangChain `DirectoryLoader` with `PyPDFLoader` (`langchain_community`)
- **Source directory:** `data/` (glob: `*.pdf`)
- **Example corpus:** `normy_zywienia_dla_populacji_polski.pdf` (Polish population nutrition norms)

Each page is extracted into LangChain `Document` objects with metadata (including `source` file paths for later citation).

### Step 2 — Chunking strategy

Deterministic splitting via `RecursiveCharacterTextSplitter`:

| Parameter | Value | Defined in |
| :--- | :--- | :--- |
| `chunk_size` | **1000** characters | `constants.CHUNK_SIZE` |
| `chunk_overlap` | **500** characters | `constants.CHUNK_OVERLAP` |

Overlap preserves continuity across page boundaries and section breaks — critical for tables and norm values split across chunks.

### Step 3 — Vectorization

- **Model:** `gemini-embedding-001` (`GoogleGenerativeAIEmbeddings`)
- Each chunk is embedded into a high-dimensional vector space for semantic similarity search.

### Step 4 — Vector store (persistent)

- **Engine:** [Chroma](https://www.trychroma.com/) via `langchain_chroma`
- **Path:** `chroma/` (`constants.CHROMA_PATH`)
- On re-index, the existing `chroma/` directory is removed and rebuilt for a clean, reproducible state.

**Run ingestion:**

```bash
python creating_database.py
```

---

## Core RAG Runtime

Query logic lives in `query_data.py` and is exposed through FastAPI in `main.py`.

### Runtime parameters

| Constant | Value | Role |
| :--- | :--- | :--- |
| `TOP_K` | **3** | Maximum chunks retrieved per question |
| `RELEVANCE_THRESHOLD` | **0.5** | Minimum similarity score for the best match |
| `GEMINI_CHAT_MODEL` | `gemini-2.5-flash` | Answer generation |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | Query + document embeddings |

### Semantic search flow (step-by-step)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. USER QUESTION                                                        │
│    POST /api/query  { "question": "..." }                               │
│    Header: X-Gemini-API-Key (client-provided)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. QUERY EMBEDDING                                                      │
│    question → gemini-embedding-001 → query vector                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. CHROMA RETRIEVAL                                                     │
│    similarity_search_with_relevance_scores(question, k=3)               │
│    • If no results OR top score < 0.5 → safe fallback message           │
│    • Else → top chunks concatenated as {context}                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. PROMPT CONSTRUCTION (strict grounding)                               │
│    ChatPromptTemplate + rules:                                          │
│    • Answer ONLY from context                                           │
│    • Respond in Polish                                                  │
│    • Admit when context lacks the answer                                │
│    • Do not invent facts                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. GENERATION                                                           │
│    gemini-2.5-flash → answer text                                       │
│    + sorted unique source filenames from chunk metadata                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         { "answer": "...", "sources": ["file.pdf", ...] }
```

### Prompt template (excerpt)

The model receives retrieved context and the user question under explicit guardrails:

```text
Jesteś asystentem dietetycznym. Odpowiedz na pytanie WYŁĄCZNIE na podstawie poniższego kontekstu
z oficjalnych dokumentów (wytyczne żywieniowe, suplementacja).

Zasady:
- Odpowiadaj zawsze po polsku.
- ...
- Nie wymyślaj faktów spoza kontekstu.

Kontekst: {context}
Pytanie: {question}
```

---

## Architecture & Cloud Deployment

The application uses a **decoupled SPA + API** architecture suitable for free-tier cloud hosting.

### System diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           DIETITIAN (Browser)                                │
│  Vue 3 SPA · Settings modal · localStorage API key · Polish clinical UI      │
└──────────────────────────────────────────────────────────────────────────────┘
         │  HTTPS                                    │
         │  GET  /api/health                         │
         │  POST /api/query + X-Gemini-API-Key       │
         ▼                                            │
┌─────────────────────────────┐                       │
│   NETLIFY (Static CDN)      │                       │
│   • Vite production build   │                       │
│   • VITE_API_BASE_URL →     │                       │
│     Render backend URL      │                       │
│   • netlify.toml SPA        │                       │
│     fallback → index.html   │                       │
└─────────────────────────────┘                       │
                                                      ▼
                              ┌───────────────────────────────────────────────┐
                              │   RENDER.COM (FastAPI + Uvicorn)              │
                              │   • main.py · CORS allow_origins=["*"]        │
                              │   • PORT from environment                     │
                              │   • Persistent chroma/ on disk (post-build)   │
                              └───────────────────────────────────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
            ┌──────────────┐        ┌─────────────────┐       ┌─────────────────┐
            │ chroma/      │        │ query_data.py   │       │ Google Gemini   │
            │ Vector DB    │        │ RAG orchestration│       │ Embeddings +    │
            │ (local disk) │        │ LangChain       │       │ 2.5 Flash       │
            └──────────────┘        └─────────────────┘       └─────────────────┘
```

### Frontend — Netlify

| Concern | Implementation |
| :--- | :--- |
| Framework | Vue 3 (Composition API) + Vite 6 |
| Styling | Tailwind CSS · clinical wellness design system |
| API base URL | `import.meta.env.VITE_API_BASE_URL` (inlined at **build time**) |
| Local dev fallback | `http://127.0.0.1:8000` when not in production |
| SPA routing | `frontend/netlify.toml` — all routes → `/index.html` (status 200) |
| Dev proxy | `vite.config.js` proxies `/api` → `127.0.0.1:8000` |

### Backend — Render (Free Tier)

| Concern | Implementation |
| :--- | :--- |
| Framework | FastAPI + Uvicorn |
| Entry | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| CORS | `CORSMiddleware` — `allow_origins=["*"]` for cross-origin Netlify → Render |
| Health | `GET /api/health` — verifies `chroma/` directory exists |

---

## API Key Management (Security Pattern)

NutriMind AI **does not require a hardcoded server-side Gemini key** for production multi-user scenarios. Instead, it uses a **bring-your-own-key (BYOK)** pattern optimized for cost control and security.

```
┌──────────────┐     Save key      ┌─────────────────────┐
│  Settings    │ ───────────────►  │  localStorage       │
│  Modal (Vue) │                   │  nutrimind_gemini_   │
└──────────────┘                   │  api_key            │
       │                           └─────────────────────┘
       │  Every POST /api/query
       ▼
┌──────────────────────────────────────────────────────┐
│  HTTP Header:  X-Gemini-API-Key: <user_key>          │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  FastAPI main.py → query_data.py                     │
│  google_api_key passed to:                         │
│    • GoogleGenerativeAIEmbeddings (retrieval)        │
│    • ChatGoogleGenerativeAI (generation)             │
└──────────────────────────────────────────────────────┘
```

| Design choice | Rationale |
| :--- | :--- |
| **Client-side storage** | Non-technical dietitians paste their own [Google AI Studio](https://aistudio.google.com/) key once |
| **Per-request header** | Key never committed to the repository; optional `GEMINI_API_KEY` in `.env` for CLI/local dev only |
| **401 if missing** | `main.py` rejects requests without `X-Gemini-API-Key` |
| **Safe localStorage read** | `useGeminiApiKey.js` wraps access in `try/catch` for privacy-mode browsers |

> **Note:** Keys in `localStorage` are appropriate for personal/portfolio demos. Enterprise deployments would move to a secure vault or OAuth proxy.

---

## Tech Stack

| Layer | Technologies | Key libraries / files |
| :--- | :--- | :--- |
| **Frontend** | Vue 3, Vite, Tailwind CSS, Lucide icons, Marked | `App.vue`, `useRagQuery.js`, `SettingsModal.vue` |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pydantic | `main.py`, `constants.py` |
| **AI / Orchestration** | LangChain Core, LangChain Google GenAI | `query_data.py`, `creating_database.py` |
| **Embeddings & LLM** | Google `gemini-embedding-001`, `gemini-2.5-flash` | `GoogleGenerativeAIEmbeddings`, `ChatGoogleGenerativeAI` |
| **Vector store** | ChromaDB (persistent, on-disk) | `langchain_chroma`, `chroma/` |
| **Document ingestion** | PyPDFLoader, RecursiveCharacterTextSplitter | `langchain_community`, `langchain_text_splitters` |
| **Hosting** | Netlify (SPA) + Render (API) | `netlify.toml`, `PORT` env on Render |

---

## Project Structure

```text
rag/
├── constants.py              # Shared RAG config (chunk sizes, models, paths)
├── creating_database.py    # PDF → chunks → Chroma ingestion pipeline
├── query_data.py             # Core RAG engine (retrieval + generation + CLI)
├── main.py                   # FastAPI app, CORS, health + query endpoints
├── requirements.txt
├── data/                     # Authoritative PDF corpus (not committed: large files)
│   └── normy_zywienia_dla_populacji_polski.pdf
├── chroma/                   # Generated vector store (gitignored)
└── frontend/
    ├── netlify.toml          # SPA redirect rules
    ├── vite.config.js        # Dev server + /api proxy
    ├── .env.example          # VITE_API_BASE_URL template
    └── src/
        ├── App.vue
        ├── config/api.js       # Production vs dev API base URL
        ├── composables/
        │   ├── useRagQuery.js
        │   ├── useGeminiApiKey.js
        │   └── useTypewriter.js
        ├── components/       # HeaderHero, QueryInput, AnswerCard, …
        └── utils/errors.js   # Localized API error mapping
```

---

## Prerequisites & Quick Start

### Prerequisites

| Requirement | Version |
| :--- | :--- |
| Python | 3.11+ |
| Node.js | 18+ |
| Gemini API key | [Google AI Studio](https://aistudio.google.com/) |

### 1 — Clone & install backend

```bash
pip install -r requirements.txt
```

Optional: create `.env` for CLI-only usage:

```bash
cp .env.example .env
# GEMINI_API_KEY=your_key_here
```

### 2 — Index your PDF corpus

Place authoritative PDFs in `data/`, then build the vector database:

```bash
python creating_database.py
```

Expected output: chunk count logged, then `Baza danych gotowa i zapisana na dysku!`

### 3 — Start the API

```bash
python main.py
```

Server: **http://127.0.0.1:8000**

### 4 — Verify health

```bash
curl http://127.0.0.1:8000/api/health
```

Example response when `chroma/` exists:

```json
{
  "status": "ok",
  "message": "Połączono z bazą wiedzy Chroma"
}
```

### 5 — Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

1. Click the **Settings** (gear) icon → paste your Gemini API key → **Save**
2. Ask a clinical nutrition question (UI in Polish)
3. Review the AI answer and **source document badges**

### 6 — CLI alternative (no UI)

```bash
python query_data.py "Jakie są zalecane normy białka?"
```

Uses `GEMINI_API_KEY` from `.env` when no header is available.

---

## API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Checks whether `chroma/` exists; returns `ok` or `degraded` |
| `POST` | `/api/query` | RAG query — body: `{ "question": "string" }` |

### `POST /api/query`

**Headers**

| Header | Required | Description |
| :--- | :--- | :--- |
| `Content-Type` | Yes | `application/json` |
| `X-Gemini-API-Key` | Yes | User’s Gemini API key |

**Response**

```json
{
  "answer": "…",
  "sources": ["normy_zywienia_dla_populacji_polski.pdf"]
}
```

---

## Production Deployment

### Render (backend)

| Setting | Value |
| :--- | :--- |
| Build command | `pip install -r requirements.txt && python creating_database.py` |
| Start command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Environment | `PORT` (injected by Render) |

Ensure `chroma/` is built during deploy or persisted on disk.

### Netlify (frontend)

| Setting | Value |
| :--- | :--- |
| Base directory | `frontend` |
| Build command | `npm run build` |
| Publish directory | `frontend/dist` |
| Environment variable | `VITE_API_BASE_URL=https://<your-render-app>.onrender.com` |

Rebuild after changing `VITE_API_BASE_URL` — Vite inlines env vars at **build time**, not runtime.

---

## What I Learned & Engineering Takeaways

### 1 — From generic loaders to authoritative PDF pipelines

The ingestion path evolved from ad-hoc text sources to a **PDF-first pipeline** using `PyPDFLoader` and `DirectoryLoader`, targeting real clinical guideline documents. Chunking parameters (`1000` / `500`) were tuned for dense nutritional tables and normative prose.

### 2 — Defensive error handling across the stack

| Layer | Pattern |
| :--- | :--- |
| **API** | `main.py` wraps query execution in `try/except`, maps failures to HTTP 500 with structured `detail` |
| **Validation** | Custom `RequestValidationError` handler returns Polish-friendly 422 messages |
| **Client** | `utils/errors.js` normalizes network failures and status codes for the Vue UI |
| **Browser storage** | `getGeminiApiKey()` uses `try/catch` when `localStorage` is blocked |

Production PDF pipelines benefit from **per-file ingestion guards** (skip corrupted streams, log and continue) — the natural next hardening step on top of the current `PyPDFLoader` foundation.

### 3 — CORS, decoupled hosting, and environment-aware clients

- Configured **FastAPI CORS** for a Netlify origin talking to a Render backend (`allow_origins=["*"]`, `allow_credentials=False` with wildcard origins).
- Implemented **build-time vs runtime** API URL resolution in `frontend/src/config/api.js`:
  - **Development:** `VITE_API_BASE_URL` or fallback `http://127.0.0.1:8000`
  - **Production:** strictly `VITE_API_BASE_URL` (no silent localhost fallback)
- **Vite dev proxy** avoids CORS friction during local full-stack development.

### 4 — BYOK header pattern for serverless-friendly AI apps

Designed a **client-injected `X-Gemini-API-Key`** flow so the backend stays stateless regarding billing keys — ideal for portfolio demos, dietitian-owned keys, and Render free-tier deployments without shared secret sprawl.

### 5 — SPA deployment discipline on Netlify

`netlify.toml` ensures Vue Router-less deep links still resolve:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## License & Disclaimer

This project is intended for **educational and portfolio demonstration** purposes.

> **Medical disclaimer:** NutriMind AI outputs are grounded in indexed documents but **do not replace** professional judgment, licensed dietetic consultation, or physician oversight. Always verify recommendations against primary sources.

---

<p align="center">
  <strong>NutriMind AI</strong> — Trust your corpus. Cite your sources. Ship production RAG.
</p>
