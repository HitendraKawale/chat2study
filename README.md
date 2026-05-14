
# Chat2Study

Chat2Study turns long AI chats into structured study assets:

- preserved artifacts (HTML, text, screenshot, PDF)
- vector-indexed chunks for semantic search
- rendered markdown study notes
- interactive visual concept maps

You give it a chat URL you are authorized to access. Chat2Study captures the page, stores artifacts, indexes the content, and lets you search or ask grounded questions over it. For dense technical content it generates study notes and concept-map style visual notes.

---

## Current status

### Implemented

- JWT-based auth (register, login, protected routes)
- Next.js 15 App Router frontend with nav, login/register pages
- FastAPI backend with full REST API
- PostgreSQL + pgvector persistence
- MinIO-backed artifact storage
- Playwright capture pipeline
- LangGraph 10-node ingestion workflow
- Multi-provider abstraction (Ollama, OpenAI, Anthropic, Google)
- Semantic chunk retrieval
- Grounded Q&A
- Markdown study notes with proper rendering + `.md` download
- Visual notes with dagre-layouted, draggable React Flow graph
- GitHub Actions CI

### Not yet implemented

- Background worker deployment (Celery / queue-based async ingestion)
- Browser extension ingestion
- Shareable study pages
- Citations in notes and Q&A answers
- Per-user chat scoping (auth exists, data is currently global)
- Production cloud deployment

---

## Tech stack

### Frontend
- Next.js 15, React 19, TypeScript
- Tailwind CSS v4
- React Flow (`@xyflow/react`) + dagre layout
- `react-markdown` + `remark-gfm`

### Backend
- FastAPI, SQLAlchemy 2, Alembic, Psycopg 3
- LangChain, LangGraph
- `python-jose` (JWT), `bcrypt` (passwords)

### Data / infra
- PostgreSQL + pgvector
- Redis (configured, used for future queue)
- MinIO (S3-compatible local object storage)
- Docker / Docker Compose

### Capture / AI
- Playwright (Chromium)
- Google Gemini (recommended free option)
- OpenAI, Anthropic, Ollama (all supported)

### Tooling
- pnpm, uv, Ruff, GitHub Actions

---

## Architecture overview

```text
[ Browser ]
    |
    v
[ Next.js App Router ]  ──── JWT cookie auth ────
    |
    v  (REST + Bearer token)
[ FastAPI ]
    |
    ├── PostgreSQL + pgvector  (chats, chunks, notes, jobs, users)
    ├── MinIO / S3             (raw_html, visible_text, screenshot, PDF)
    └── LangGraph ingestion workflow
            ├── Playwright capture
            ├── Artifact persistence
            ├── Chunk + embed (Google / OpenAI / Ollama)
            ├── Complexity scoring
            ├── Study notes generation (LLM)
            └── Visual notes generation (LLM → React Flow)
```

---

## Local development setup

### Prerequisites

- Node.js 22+
- pnpm 10+
- Python 3.11+
- uv
- Docker + Docker Compose
- A Google AI Studio API key (free) **or** Ollama for fully local use

---

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/chat2study.git
cd chat2study
```

---

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in at minimum:

```env
# Free option — get your key at aistudio.google.com/apikey
GOOGLE_API_KEY=your-key-here
DEFAULT_CHAT_PROVIDER=google
DEFAULT_EMBEDDING_PROVIDER=google
GOOGLE_CHAT_MODEL=gemini-2.5-flash
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001

# Auth secret — generate with: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=change-me
```

For the web app:

```bash
cp apps/web/.env.local.example apps/web/.env.local
```

---

### 3. Start infrastructure

```bash
pnpm infra:up
```

This starts PostgreSQL + pgvector, Redis, and MinIO.

| Service | URL |
|---|---|
| Web app | http://localhost:3000 |
| API + Swagger | http://localhost:8000/docs |
| MinIO console | http://localhost:9001 (minioadmin / minioadmin) |

---

### 4. Start the API

```bash
cd apps/api
uv sync
uv run playwright install chromium
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### 5. Start the web app

From the repo root:

```bash
pnpm install
pnpm web:dev
```

Open `http://localhost:3000` — you'll be redirected to `/login`. Register an account and you're in.

---

## AI provider options

The chat and embedding providers are independently configurable via env vars. No code changes needed.

### Google AI Studio (recommended — free)

Get a key at **aistudio.google.com/apikey** — no credit card required.

```env
GOOGLE_API_KEY=your-key
DEFAULT_CHAT_PROVIDER=google
DEFAULT_EMBEDDING_PROVIDER=google
GOOGLE_CHAT_MODEL=gemini-2.5-flash
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001
```

### Anthropic

```env
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_CHAT_PROVIDER=anthropic
ANTHROPIC_CHAT_MODEL=claude-haiku-4-5-20251001
# Use an embedding provider separately (Google or OpenAI) — Anthropic has no embeddings API
DEFAULT_EMBEDDING_PROVIDER=google
```

### OpenAI

```env
OPENAI_API_KEY=sk-...
DEFAULT_CHAT_PROVIDER=openai
DEFAULT_EMBEDDING_PROVIDER=openai
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Ollama (fully local, free)

```bash
ollama serve
ollama pull llama3.1:8b       # recommended minimum for notes generation
ollama pull nomic-embed-text
```

```env
DEFAULT_CHAT_PROVIDER=ollama
DEFAULT_EMBEDDING_PROVIDER=ollama
OLLAMA_CHAT_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
```

> **Note:** If you switch embedding models after indexing chats, re-index existing chats via `POST /api/v1/chats/{id}/index` — vectors from different models are not compatible.

---

## Environment variables reference

### Core

```env
PROJECT_NAME=Chat2Study
NODE_ENV=development
SECRET_KEY=            # JWT signing secret (required — generate a random hex string)
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7
```

### Database

```env
DATABASE_URL=postgresql+psycopg://chat2study:chat2study@localhost:5432/chat2study
```

### Object storage

```env
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=chat2study
S3_FORCE_PATH_STYLE=true
```

### Providers

```env
DEFAULT_CHAT_PROVIDER=google          # google | openai | anthropic | ollama
DEFAULT_EMBEDDING_PROVIDER=google     # google | openai | ollama

GOOGLE_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

GOOGLE_CHAT_MODEL=gemini-2.5-flash
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
ANTHROPIC_CHAT_MODEL=claude-haiku-4-5-20251001
OLLAMA_CHAT_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
```

### Indexing / retrieval / notes

```env
EMBEDDING_DIMENSIONS=768
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=5
NOTES_CONTEXT_CHAR_LIMIT=80000
```

### Capture

```env
PLAYWRIGHT_HEADLESS=true
LOCAL_ARTIFACT_STAGING_DIR=.cache/artifacts
```

---

## How ingestion works

The pipeline is a 10-node LangGraph state machine:

1. **load_chat** — fetch chat + source metadata from DB
2. **select_providers** — resolve chat and embedding providers from config
3. **plan_capture** — choose browser strategy (authenticated for Claude.ai / ChatGPT / Gemini, generic otherwise)
4. **execute_capture** — Playwright headless capture (HTML, text, screenshot, PDF)
5. **persist_artifacts** — upload all artifacts to MinIO
6. **index_chat** — chunk text, embed with configured provider, store in pgvector
7. **classify_complexity_seed** — score content density to decide whether to auto-generate notes
8. **generate_study_notes** — LLM markdown notes (if complexity threshold met)
9. **generate_visual_notes** — LLM JSON graph for React Flow (if threshold met)
10. **build_result_payload** — assemble final workflow result

Notes auto-generation can be triggered manually from the UI or API regardless of complexity score.

---

## API surface

All routes require a `Authorization: Bearer <token>` header except `/auth/register` and `/auth/login`.

### Auth

```
POST /api/v1/auth/register    { email, name, password } → { access_token }
POST /api/v1/auth/login       { email, password }       → { access_token }
GET  /api/v1/auth/me                                    → UserResponse
```

### System

```
GET /api/v1/health
GET /api/v1/providers
```

### Chats

```
POST /api/v1/chats             create a chat record
GET  /api/v1/chats             list recent chats (up to 50)
GET  /api/v1/chats/{id}        get a single chat
```

### Ingestion / jobs

```
POST /api/v1/chats/{id}/ingest    run the full ingestion pipeline
GET  /api/v1/jobs/{id}            poll job status
```

### Artifacts

```
GET /api/v1/chats/{id}/artifacts
GET /api/v1/chats/{id}/artifacts/{artifact_id}/download
```

### Indexing / retrieval

```
POST /api/v1/chats/{id}/index     re-index (use after switching embedding providers)
POST /api/v1/chats/{id}/search    { query, top_k } → semantic chunk results
POST /api/v1/chats/{id}/ask       { question, top_k } → grounded LLM answer
```

### Notes

```
GET  /api/v1/chats/{id}/notes
POST /api/v1/chats/{id}/notes/generate
POST /api/v1/chats/{id}/visual-notes/generate
GET  /api/v1/chats/{id}/notes/download     → .md file download
```

---

## Frontend pages

### `/login` and `/register`

JWT-based auth. Token is stored in a cookie and sent as a Bearer header on all API requests. All other routes require a valid token (enforced by Next.js middleware).

### `/` — Dashboard

- Ingest form with progress feedback
- Recent chats list with color-coded status badges
- Links to chat detail pages

### `/chats/[chatId]` — Chat detail

- Study notes rendered with `react-markdown` (headers, code blocks, tables, lists)
- Download study notes as `.md` file
- Generate study notes / visual map buttons with spinner feedback
- Visual concept map: dagre-layouted, color-coded by node kind, draggable
- Semantic search and grounded Q&A panel
- Artifact browser with download links

---

## Build and quality checks

```bash
# Web build
pnpm web:build

# Web lint
pnpm web:lint

# API lint
cd apps/api && uv run ruff check .

# API format
cd apps/api && uv run ruff format .

# New migration after model changes
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

---

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push and PRs:

- API: dependency install → Ruff lint → import check
- Web: dependency install → production build

---

## Docker

Dockerfiles exist for both services:

```bash
docker build -f apps/api/Dockerfile -t chat2study-api .
docker build -f apps/web/Dockerfile -t chat2study-web .
```

---

## Deployment architecture

This app cannot be deployed as a single unit because Playwright requires a persistent Linux environment with Chromium — incompatible with serverless platforms.

| Component | Recommended host | Notes |
|---|---|---|
| Next.js frontend | Vercel | Zero-config, native Next.js support |
| FastAPI backend | Railway / Render / Fly.io | Needs Dockerfile, persistent process for Playwright |
| PostgreSQL | Neon (free) or Railway | Enable the pgvector extension |
| MinIO / S3 | Cloudflare R2 (free 10 GB) or AWS S3 | Set `S3_FORCE_PATH_STYLE=false` for real S3 |
| Redis | Upstash (free tier) | Used for future background jobs |

Environment variables to change for production:

```env
NODE_ENV=production
SECRET_KEY=<strong random secret>
DATABASE_URL=<managed postgres URL>
REDIS_URL=<upstash redis URL>
S3_ENDPOINT=<r2 or s3 endpoint>
S3_FORCE_PATH_STYLE=false
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

---

## Troubleshooting

### Notes not auto-generating

The complexity scorer may have rated the page as too simple. Use the **Generate** buttons in the UI or call the API endpoints directly — they always run regardless of score.

### Playwright timeout on modern sites

Some pages never reach `networkidle` (analytics, websockets). The capture waits for `domcontentloaded`, tries `load`, tries `networkidle` briefly, then continues regardless.

### Switching embedding providers

Vectors from different models are in different spaces and are not compatible. After changing `DEFAULT_EMBEDDING_PROVIDER`, re-index existing chats:

```bash
curl -X POST http://localhost:8000/api/v1/chats/CHAT_ID/index \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### zsh bracket escaping

When creating Next.js dynamic routes in zsh, quote paths with square brackets:

```bash
mkdir -p 'apps/web/app/chats/[chatId]'
```

---

## Roadmap

- Background worker deployment (async ingestion with Celery)
- Per-user chat scoping
- Browser extension for one-click ingestion
- Shareable study pages
- Citations in answers and notes
- Export notes as PDF / slides
- Production deployment guide

---

## License

Released under the MIT License. See [LICENSE](./LICENSE) for the full text.
