# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chat2Study is a monorepo that ingests long AI chats and transforms them into:
- Preserved artifacts (HTML, text, screenshots, PDFs)
- Vector-indexed chunks for semantic search
- Generated markdown study notes
- Visual concept maps with React Flow

The system captures authorized chat URLs, extracts content, embeds chunks into PostgreSQL with pgvector, and generates AI-powered study materials. Multi-provider support (Ollama, OpenAI, Anthropic, Google Gemini) allows flexible model selection.

## Architecture Overview

**High-level data flow:**
```
Next.js Web (React 19, Tailwind v4) ↔ FastAPI Backend (SQLAlchemy 2, LangChain/LangGraph)
                                            ↓
                    PostgreSQL + pgvector (chunks, embeddings)
                                            ↓
                    MinIO S3-compatible (artifacts: HTML, text, PNG, PDF)
                                            ↓
                    Playwright (capture) → LangGraph workflow (orchestration)
```

**Ingestion workflow (LangGraph):**
The `IngestionWorkflow` in `apps/api/app/workflows/` executes a 10-node pipeline:
1. `load_chat` - Fetch chat metadata from DB
2. `select_providers` - Resolve LLM/embedding providers from config
3. `plan_capture` - Choose browser strategy (authenticated for Claude.ai/ChatGPT/Gemini, generic otherwise)
4. `execute_capture` - Playwright headless browser capture
5. `persist_artifacts` - Store HTML/text/screenshot/PDF to MinIO
6. `index_chat` - Chunk text and embed with selected provider
7. `classify_complexity_seed` - Score content complexity for note generation
8. `generate_study_notes` - LLM markdown notes (conditional on complexity)
9. `generate_visual_notes` - LLM JSON graph structure for React Flow rendering
10. `build_result_payload` - Assemble response with all metadata

**Database schema:**
- `users` - Multi-user scaffolding (not yet implemented)
- `sources` - URLs with domain/type tracking
- `chats` - Chat records with status and complexity_score
- `artifacts` - S3 references (type, key, MIME, size)
- `chunks` - pgvector embeddings with ordinal position and metadata
- `jobs` - Ingestion job records (queued/running/completed/failed)
- `notes` - Study notes (markdown) and visual notes (JSON) per chat

**API surface (FastAPI v1):**
- Health & system: `/api/v1/health`, `/api/v1/providers`
- Chats: `POST /chats`, `GET /chats`
- Ingestion: `POST /chats/{id}/ingest`, `GET /jobs/{id}`
- Artifacts: `GET /chats/{id}/artifacts`, `GET /chats/{id}/artifacts/{id}/download`
- Retrieval: `POST /chats/{id}/search`, `POST /chats/{id}/ask` (vector + LLM Q&A)
- Notes: `GET /chats/{id}/notes`, `POST /chats/{id}/notes/generate`, `POST /chats/{id}/visual-notes/generate`
- Indexing: `POST /chats/{id}/index` (manual re-indexing)

**Provider factory pattern:**
The `ProviderFactory` in `apps/api/app/services/providers.py` abstracts LangChain model selection:
- Chat models: Ollama, OpenAI, Anthropic, Google (aliases: claude=anthropic, gemini=google)
- Embedding models: Ollama, OpenAI, Google (default: ollama/nomic-embed-text)
- Configuration via env vars: `DEFAULT_CHAT_PROVIDER`, `OPENAI_CHAT_MODEL`, `ANTHROPIC_CHAT_MODEL`, etc.

**Web frontend:**
- Next.js 15 App Router with dynamic routes (`/chats/[chatId]`)
- Dashboard: ingest form + recent chats list
- Chat detail: artifact browser, semantic search, Q&A, note generation actions, React Flow visual graph
- Async params required in dynamic routes (Next.js 15+): `params: Promise<{ chatId: string }>`

## Setup & Development Commands

### Prerequisites
- Node.js 22+ (for web)
- Python 3.11+ with uv (for API)
- Docker + Docker Compose (for services)
- Ollama (optional, for local free models)

### Initialize local environment

```bash
# Root setup
cp .env.example .env
pnpm install

# Web app
cp apps/web/.env.local.example apps/web/.env.local

# API
cd apps/api
uv sync
uv run playwright install chromium
uv run alembic upgrade head
```

### Start infrastructure

```bash
# Start all services (PostgreSQL, Redis, MinIO)
pnpm infra:up

# View running services
pnpm infra:ps

# Tail logs
pnpm infra:logs

# Stop all
pnpm infra:down
```

Default local URLs:
- Web app: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- MinIO console: `http://localhost:9001` (minioadmin/minioadmin)
- Redis: localhost:6379
- PostgreSQL: localhost:5432 (chat2study/chat2study)

### Start development servers

**API (from `apps/api`):**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Web app (from repo root):**
```bash
pnpm web:dev
```

Both will hot-reload on file changes.

### Common development commands

**API:**
```bash
# Lint (Ruff)
cd apps/api
uv run ruff check .

# Format
uv run ruff format .

# Run migrations
uv run alembic upgrade head
uv run alembic downgrade -1

# Create new migration (after model changes)
uv run alembic revision --autogenerate -m "description"

# Import sanity check
uv run python -c "from app.main import app; print(app.title)"
```

**Web:**
```bash
# Lint
pnpm web:lint

# Production build
pnpm web:build

# Start production server
pnpm web:start
```

### CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push to main and PRs:
- **API:** dependency install, Ruff lint, import check
- **Web:** dependency install, Next.js production build

No tests defined yet; project is in phase 7 (frontend integration).

## Key Files & Patterns

**Backend entry:**
- `apps/api/app/main.py` - FastAPI app initialization, CORS, router inclusion
- `apps/api/app/core/config.py` - Pydantic settings with env var aliases (e.g., `OPENAI_CHAT_MODEL` → `openai_chat_model`)
- `apps/api/app/db/session.py` - SQLAlchemy session management

**Ingestion orchestration:**
- `apps/api/app/workflows/ingestion_graph.py` - LangGraph state machine (10 nodes, linear edges)
- `apps/api/app/workflows/ingestion_state.py` - Typed state dict for workflow
- `apps/api/app/workflows/ingestion_nodes.py` - Individual node implementations
- `apps/api/app/services/job_runner.py` - Synchronous job runner (no async workers yet)

**Capture & storage:**
- `apps/api/app/services/capture/browser_capture.py` - Playwright-based page capture
- `apps/api/app/services/object_storage.py` - MinIO S3 client wrapper
- `apps/api/app/services/artifact_manager.py` - Persist/retrieve artifacts from S3

**Indexing & retrieval:**
- `apps/api/app/services/indexing.py` - Text chunking (recursive char, configurable size/overlap) + embedding
- `apps/api/app/services/retrieval.py` - Semantic similarity search via pgvector
- `apps/api/app/services/qa.py` - Grounded Q&A (retrieve chunks, pass to LLM)

**Notes generation:**
- `apps/api/app/services/notes.py` - Study notes (markdown) and visual notes (JSON with nodes/edges) generation
- Uses LLM with injected context to generate structure + content

**Frontend structure:**
- `apps/web/app/page.tsx` - Dashboard with ingest form and chat list
- `apps/web/app/chats/[chatId]/page.tsx` - Chat detail with artifacts, search, Q&A, visual notes
- `apps/web/components/` - Reusable UI components (ingest-form, qa-panel, visual-notes-graph, etc.)
- `apps/web/lib/api.ts` - Typed API client (apiFetch wrapper)

## Configuration & Environment

**Critical env vars:**
```env
# Providers (default: ollama for both)
DEFAULT_CHAT_PROVIDER=ollama|openai|anthropic|google
DEFAULT_EMBEDDING_PROVIDER=ollama|openai|google
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_CHAT_MODEL=gpt-4|gpt-3.5-turbo
ANTHROPIC_CHAT_MODEL=claude-opus-4-1|claude-3.5-sonnet
GOOGLE_CHAT_MODEL=gemini-pro
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# Database & cache
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=redis://localhost:6379/0

# Object storage (MinIO local, or S3 compatible)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=chat2study
S3_FORCE_PATH_STYLE=true

# Indexing & retrieval tuning
EMBEDDING_DIMENSIONS=768  # Must match embedding model output
CHUNK_SIZE=1200          # Characters per chunk
CHUNK_OVERLAP=200        # Overlap for context preservation
RETRIEVAL_TOP_K=5        # Results returned in search/ask
NOTES_CONTEXT_CHAR_LIMIT=16000

# Playwright
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_AUTH_STATE_PATH=playwright/.auth/default.json
LOCAL_ARTIFACT_STAGING_DIR=.cache/artifacts
```

**Ollama local setup:**
```bash
ollama serve  # In another terminal
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

## Important Patterns & Conventions

**Monorepo structure:**
- `apps/api` - FastAPI backend
- `apps/web` - Next.js frontend
- `workers/` - Future: background job workers (ingest_worker, index_worker, notes_worker)
- `packages/` - Shared code (ui components, types)
- `infra/` - Docker Compose overrides, init scripts, deployment helpers

**Pydantic models vs SQLAlchemy models:**
- Schemas in `apps/api/app/schemas/` are Pydantic request/response DTO classes
- Models in `apps/api/app/db/models.py` are SQLAlchemy ORM classes
- Keep them separate; schemas transform ORM objects for API responses

**Error handling:**
- API routes catch specific exceptions (ValueError → 404, generic → 500)
- Workflow nodes propagate exceptions; job runner catches and logs to Job.error_message
- Web app handles 404 with notFound() and errors with error state UI

**Type safety:**
- Web uses TypeScript strict mode; API uses Python 3.11+ type hints
- Pydantic v2 with model_validate() for ORM → schema conversion
- Next.js 15 dynamic params are async: `params: Promise<{ chatId: string }>`

**Artifact storage:**
- All artifacts keyed by chat_id + type (e.g., `{chat_id}/raw_html`, `{chat_id}/screenshot_png`)
- Staged artifacts stored locally in `.cache/artifacts` before S3 upload
- Download endpoint streams from S3

**Notes generation complexity heuristic:**
- Calculated during ingestion based on token count + content density
- Only auto-generates notes if complexity score exceeds threshold
- Manual generation endpoints always available via API or UI buttons

## Known Issues & Workarounds

**Next.js 15 dynamic routes in zsh:**
Quote or escape route param names to avoid glob expansion:
```bash
mkdir -p 'apps/web/app/chats/[chatId]'
touch 'apps/web/app/chats/[chatId]/page.tsx'
```

**Playwright networkidle timeout:**
Some pages with analytics/polling never reach `networkidle`. Capture logic waits for `domcontentloaded`, tries `load`, attempts `networkidle` briefly, but continues even if `networkidle` never fires.

**Notes showing null:**
Simple pages (e.g., example.com) may not auto-generate notes if complexity score is low. Use manual generation buttons or API endpoints to force generation.

**Ollama indexing failures:**
Ensure Ollama is running and embedding model exists:
```bash
ollama list
ollama pull nomic-embed-text  # If missing
```

## Roadmap & Future Work

**Not yet implemented:**
- Authentication & multi-user support (User model scaffolded, not wired)
- Background worker deployment (Celery workers planned in workers/)
- Browser extension ingestion
- Shareable study pages
- Citations in notes/answers
- Production cloud deployment guide (structure is ready for ECS/S3/RDS/managed PostgreSQL)

**Current phase:** Phase 7 (Frontend integration) – all core features functional locally, scaling for production pending.
