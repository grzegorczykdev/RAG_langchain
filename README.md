# 🤖 DocuMind AI — Full-Stack RAG Platform

DocuMind AI is a production-ready, modern **Retrieval-Augmented Generation (RAG)** application that allows users to have intelligent, context-aware conversations with their private document repositories. By combining a high-performance **FastAPI** backend with a reactive **Vue 3** enterprise-grade frontend, the platform eliminates AI hallucinations by anchoring LLM responses strictly within verified local datasets.

---

## 💡 What I Learned & Project Reflections

Building this full-stack RAG application provided deep hands-on experience with modern AI orchestration and web engineering:

- **Vector Embeddings & Semantic Search:** Mastered the pipeline of ingestion, data cleaning, and deterministic chunking (`chunk_size=1000`, `chunk_overlap=500`) using **LangChain**. Learned how to transform raw unstructured Markdown data into multi-dimensional vector spaces using Google's `gemini-embedding-001`.
- **Cost-Effective AI Orchestration:** Successfully migrated from legacy OpenAI pipelines to **Google Gemini APIs** (`gemini-2.5-flash`), drastically lowering computational costs while preserving extreme speed and high context-retrieval fidelity.
- **Modern Full-Stack Architecture:** Implemented a clean separation of concerns by coupling an asynchronous, lightweight Python API layer with a modern, reactive SPA (Single Page Application) powered by Vue 3's Composition API and Tailwind CSS.

---

## 🎯 Use Cases: Where This Tool Shines

This architecture is highly scalable and directly solves business-critical problems across multiple domains:

- **Internal Knowledge Bases:** Transform messy corporate wikis, compliance PDFs, or developer handbooks into a searchable, interactive chatbot.
- **Automated Customer Support:** Feed the system product manuals and FAQs to create a support agent that replies with 100% accuracy, backed by direct file sources.
- **Smart Research Assistant:** Analyze thousands of pages of academic papers, medical transcripts, or legal briefs in seconds, complete with automatic source attribution.

---

## 🛠️ Technical Stack

| Layer | Technology | Key Purpose |
| :--- | :--- | :--- |
| **Frontend** | Vue 3 (Composition API), Vite, Tailwind CSS | Reactive UI, modern dark-mode glassmorphism, instant state management |
| **Backend** | FastAPI, Python 3.11+ | High-concurrency async endpoints, lightweight API routing |
| **AI Layer** | LangChain, Google Gemini API | Chunking strategies, prompt engineering, LLM orchestration |
| **Vector Store** | Chroma DB | On-disk semantic storage, ultra-fast vector similarity queries |

---

## 📁 Project Structure

```text
rag/
├── main.py                 # Async FastAPI server & CORS orchestration
├── query_data.py           # Core RAG engine (encapsulated API & CLI execution)
├── creating_database.py    # Deterministic vector indexing pipeline (Chroma)
├── requirements.txt        # Backend dependencies
├── data/                   # Private source knowledge base (.md files)
├── chroma/                 # Embedded vector database (auto-generated)
└── frontend/               # Single Page Application
    ├── src/
    │   ├── App.vue         # Main layout & view injection
    │   ├── components/     # Reusable UI widgets (chat, search, source badges)
    │   └── composables/    # State management & API fetch layers
    └── package.json
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** and **Node.js 18+**
- A valid `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/)

Copy the example env file and add your key:

```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```

### 1. Backend — ingestion & setup

Initialize your environment, install Python dependencies, and vectorize documents in `data/`:

```bash
pip install -r requirements.txt

# Seed, chunk, and embed your source documents inside data/
python creating_database.py

# Start the API server
python main.py
```

The API runs at **http://127.0.0.1:8000**

| Endpoint | Description |
| :--- | :--- |
| `GET /api/health` | Checks database health and vector persistence |
| `POST /api/query` | Query entrypoint — body: `{ "question": "string" }` → `{ "answer": "string", "sources": [] }` |

### 2. Frontend — development UI

In a **second terminal**, start the Vue dev server:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — Vite proxies `/api` requests to the FastAPI backend.

### 3. Production build (optional)

```bash
cd frontend
npm run build
npm run preview
```

---

## 🖥️ Alternative: CLI execution

Prefer evaluating the core RAG runtime from the terminal? Skip the web UI and query directly:

```bash
python query_data.py "How does Dorothy meet the Wizard?"
```

---

*Developed with a focus on modern AI integration patterns, performance optimizations, and semantic precision.*
