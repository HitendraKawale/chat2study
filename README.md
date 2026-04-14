
# Chat2Study

Chat2Study is a production-oriented monorepo that turns long AI chats into:

- preserved artifacts
- searchable RAG-ready knowledge
- markdown study notes
- visual study maps

You give it a chat URL that you are authorized to access. Chat2Study captures the page, stores artifacts, indexes the content, and lets you search or ask grounded questions over the captured chat. For dense technical content, it can also generate study notes and visual notes.

---

## Why this project exists

Long AI chats often contain useful decisions, explanations, code, architecture discussions, and research notes, but they are hard to revisit and even harder to study properly.

Chat2Study solves that by turning a chat into a structured study asset:

- **capture** the original page
- **preserve** HTML, text, screenshot, and PDF
- **index** the content into vector-searchable chunks
- **retrieve** relevant chunks for semantic search and Q&A
- **generate** study notes
- **render** visual notes as concept maps

This project was built as a real product foundation, not just a local script.

---

## Current status

### Implemented

- Next.js App Router frontend
- FastAPI backend
- PostgreSQL + pgvector persistence
- MinIO-backed local artifact storage
- Playwright capture pipeline
- LangGraph ingestion workflow
- LangChain provider abstraction
- semantic retrieval
- grounded Q&A
- study notes generation
- visual notes JSON generation
- visual notes graph rendering in the frontend
- GitHub Actions CI
- Dockerfiles for web and API

### Not finished yet

- production cloud deployment guide
- auth / multi-user support
- background worker deployment
- browser extension
- shareable study pages
- citations in note output
- stronger provider-specific extraction logic for each chat platform

---

## Core features

### 1. Chat ingestion
Paste a chat URL and Chat2Study will:

- create a chat record
- run ingestion
- capture the page with Playwright
- extract visible text
- save raw HTML
- save a full-page screenshot
- save a PDF snapshot

### 2. Artifact persistence
Artifacts are stored in S3-compatible object storage.

Current local setup uses **MinIO**.

Stored artifact types include:

- `raw_html`
- `visible_text`
- `screenshot_png`
- `snapshot_pdf`

### 3. Vector indexing
Captured text is chunked and embedded into a `pgvector`-backed `chunks` table.

This enables:

- semantic chunk search
- grounded Q&A
- note generation from indexed context

### 4. Provider abstraction
Chat and embedding providers are configurable.

Supported chat providers:
- Ollama
- OpenAI
- Anthropic
- Google Gemini

Supported embedding providers:
- Ollama
- OpenAI
- Google Gemini

### 5. Study notes
The backend can generate markdown study notes with sections like:

- summary
- core ideas
- important decisions
- key terms
- open questions
- suggested follow-ups

### 6. Visual notes
The backend can also generate structured visual notes JSON:

- summary cards
- concept nodes
- graph edges
- suggested learner questions

The frontend renders this as a graph using React Flow.

### 7. Retrieval and grounded Q&A
You can:

- run semantic chunk search
- ask questions over an indexed chat
- see retrieved chunks used for answering

---

## Architecture overview

```text
[ Next.js Web App ]
        |
        v
[ FastAPI API ]
        |
        +------> [ Redis ]              (planned worker usage / future queue integration)
        |
        +------> [ PostgreSQL + pgvector ]
        |
        +------> [ MinIO / S3-compatible object storage ]
        |
        +------> [ Playwright capture ]
        |
        +------> [ LangGraph ingestion workflow ]
                     |
                     +--> capture
                     +--> persist artifacts
                     +--> index chunks
                     +--> generate notes
                     +--> generate visual notes
````



## Tech stack

### Frontend

* Next.js 15
* React 19
* TypeScript
* Tailwind CSS v4
* React Flow (`@xyflow/react`)

### Backend

* FastAPI
* SQLAlchemy 2
* Alembic
* Psycopg 3
* LangChain
* LangGraph

### Data / infra

* PostgreSQL
* pgvector
* Redis
* MinIO
* Docker / Docker Compose

### Capture / AI

* Playwright
* Ollama
* OpenAI
* Anthropic
* Google Gemini

### Tooling

* pnpm
* uv
* Ruff
* GitHub Actions

---

## Monorepo structure

```text
chat2study/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   │   └── capture/
│   │   │   └── workflows/
│   │   ├── alembic/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   └── web/
│       ├── app/
│       ├── components/
│       ├── lib/
│       ├── types/
│       ├── Dockerfile
│       ├── package.json
│       └── next.config.ts
├── workers/
│   ├── ingest_worker/
│   ├── index_worker/
│   └── notes_worker/
├── packages/
│   ├── ui/
│   └── shared-types/
├── infra/
│   ├── compose/
│   │   └── postgres/
│   │       └── init/
│   └── scripts/
├── docs/
├── .github/
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
├── docker-compose.yml
├── package.json
├── pnpm-workspace.yaml
└── .env.example
```

---

## How the ingestion workflow works

The ingestion pipeline is orchestrated with **LangGraph**.

### Current flow

1. load chat metadata
2. select chat provider + embedding provider
3. plan capture strategy
4. capture the page using Playwright
5. persist artifacts
6. index the text into chunks + embeddings
7. compute a complexity score
8. optionally generate study notes
9. optionally generate visual notes
10. build final workflow result payload

### Complexity behavior

Auto-note generation depends on the computed complexity score.

That means:

* simple pages may not auto-generate notes
* dense technical pages are more likely to trigger note generation
* you can still trigger note generation manually from the UI or API

---

## Local development setup

## Prerequisites

Make sure you have:

* Node.js 22+
* pnpm 10+
* Python 3.11+
* uv
* Docker + Docker Compose
* Ollama installed locally if you want free local model testing

---

## 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/chat2study.git
cd chat2study
```

---

## 2. Configure environment files

### Root environment

```bash
cp .env.example .env
```

### Web environment

```bash
cp apps/web/.env.local.example apps/web/.env.local
```

---

## 3. Start local infra

```bash
docker compose up -d
docker compose ps
```

This starts:

* PostgreSQL + pgvector
* Redis
* MinIO
* MinIO bucket bootstrap

### Useful local service URLs

* Web app: `http://localhost:3000`
* API docs: `http://localhost:8000/docs`
* MinIO console: `http://localhost:9001`

Default MinIO credentials:

```text
username: minioadmin
password: minioadmin
```

---

## 4. Start Ollama for local model use

If you want free local testing with Ollama:

```bash
ollama serve
```

In another terminal:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Default local model configuration in this project uses:

* chat model: `llama3.2:3b`
* embedding model: `nomic-embed-text`

---

## 5. Start the API

```bash
cd apps/api
uv sync
uv run playwright install chromium
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 6. Start the web app

From the repo root:

```bash
pnpm install
pnpm web:dev
```

Open:

```text
http://localhost:3000
```

---

## Environment variables

Below are the most important environment variables.

### Core app

```env
PROJECT_NAME=Chat2Study
NODE_ENV=development
```

### Web

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
WEB_PORT=3000
```

### API

```env
API_HOST=0.0.0.0
API_PORT=8000
```

### Database

```env
POSTGRES_DB=chat2study
POSTGRES_USER=chat2study
POSTGRES_PASSWORD=chat2study
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://chat2study:chat2study@localhost:5432/chat2study
```

### Redis

```env
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0
```

### Object storage

```env
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=chat2study
AWS_DEFAULT_REGION=us-east-1
S3_FORCE_PATH_STYLE=true
```

### Playwright

```env
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_AUTH_STATE_PATH=playwright/.auth/default.json
LOCAL_ARTIFACT_STAGING_DIR=.cache/artifacts
```

### Provider selection

```env
DEFAULT_CHAT_PROVIDER=ollama
DEFAULT_EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### Provider model names

```env
OPENAI_CHAT_MODEL=
OPENAI_EMBEDDING_MODEL=
ANTHROPIC_CHAT_MODEL=
GOOGLE_CHAT_MODEL=
GOOGLE_EMBEDDING_MODEL=
OLLAMA_CHAT_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### Retrieval / indexing / notes

```env
EMBEDDING_DIMENSIONS=768
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=5
NOTES_CONTEXT_CHAR_LIMIT=16000
```

---

## Using the app

## Typical workflow

### From the web UI

1. open `http://localhost:3000`
2. paste a chat URL
3. create + ingest
4. open the chat detail page
5. inspect artifacts
6. search chunks
7. ask grounded questions
8. generate study notes manually if needed
9. generate visual notes manually if needed

### From the API

#### Health

```bash
curl http://127.0.0.1:8000/api/v1/health
```

#### Providers

```bash
curl http://127.0.0.1:8000/api/v1/providers
```

#### Create a chat

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chats" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "title": "Example capture",
    "source_type": "web_chat_url"
  }'
```

#### List chats

```bash
curl http://127.0.0.1:8000/api/v1/chats
```

#### Run ingestion

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chats/CHAT_ID/ingest"
```

#### Check artifacts

```bash
curl http://127.0.0.1:8000/api/v1/chats/CHAT_ID/artifacts
```

#### Trigger indexing manually

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chats/CHAT_ID/index"
```

#### Search indexed chunks

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chats/CHAT_ID/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this chat about?",
    "top_k": 5
  }'
```

#### Ask the chat

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chats/CHAT_ID/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Summarize the main technical decisions in this chat.",
    "top_k": 5
  }'
```

#### Generate study notes manually

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chats/CHAT_ID/notes/generate"
```

#### Generate visual notes manually

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chats/CHAT_ID/visual-notes/generate"
```

#### Fetch notes bundle

```bash
curl http://127.0.0.1:8000/api/v1/chats/CHAT_ID/notes
```

---

## API surface

### Health / system

* `GET /api/v1/health`
* `GET /api/v1/providers`

### Chats

* `POST /api/v1/chats`
* `GET /api/v1/chats`

### Ingestion / jobs

* `POST /api/v1/chats/{chat_id}/ingest`
* `GET /api/v1/jobs/{job_id}`

### Artifacts

* `GET /api/v1/chats/{chat_id}/artifacts`
* `GET /api/v1/chats/{chat_id}/artifacts/{artifact_id}/download`

### Indexing / retrieval

* `POST /api/v1/chats/{chat_id}/index`
* `POST /api/v1/chats/{chat_id}/search`
* `POST /api/v1/chats/{chat_id}/ask`

### Notes

* `GET /api/v1/chats/{chat_id}/notes`
* `POST /api/v1/chats/{chat_id}/notes/generate`
* `POST /api/v1/chats/{chat_id}/visual-notes/generate`

---

## Frontend pages

### Dashboard

The dashboard includes:

* ingest form
* recent chats list
* link into chat detail pages

### Chat detail page

The chat detail page includes:

* study notes panel
* manual note generation actions
* artifact metadata + download links
* semantic search UI
* grounded Q&A UI
* visual notes cards
* visual graph renderer

---

## Build and quality checks

## Web build

```bash
pnpm --filter @chat2study/web build
```

## API lint

```bash
cd apps/api
uv sync
uv run ruff check .
```

---

## CI

GitHub Actions currently checks:

* API dependency install
* API Ruff check
* API import sanity check
* web dependency install
* web production build

Workflow file:

```text
.github/workflows/ci.yml
```

---

## Docker

There are Dockerfiles for both services:

* `apps/api/Dockerfile`
* `apps/web/Dockerfile`

This gives you a good foundation for container-based deployment later.

### API image build

```bash
docker build -f apps/api/Dockerfile -t chat2study-api .
```

### Web image build

```bash
docker build -f apps/web/Dockerfile -t chat2study-web .
```

---

## Current development notes

### Notes may not auto-generate for simple pages

Auto note generation depends on complexity scoring.

That means:

* `example.com` or very short pages may not generate notes automatically
* manual generation endpoints and UI buttons still work

### Ollama must be running for local provider use

If you are using local Ollama providers, make sure:

```bash
ollama serve
```

and required models are installed.

### Playwright browser install is required

After Python dependencies are installed:

```bash
uv run playwright install chromium
```

---

## Troubleshooting

## zsh dynamic-route path issue

If you create a Next.js route like `[chatId]` in zsh, quote or escape the path:

```bash
mkdir -p 'apps/web/app/chats/[chatId]'
touch 'apps/web/app/chats/[chatId]/page.tsx'
```

---

## Next.js 15 route params typing

Next.js 15 App Router treats dynamic route `params` as async in page props.

Use:

```tsx
export default async function Page({
  params,
}: {
  params: Promise<{ chatId: string }>;
}) {
  const { chatId } = await params;
}
```

---

## Playwright timeout on modern sites

Some pages never become truly `networkidle` because of analytics, polling, or websockets.

The capture logic was adjusted to:

* wait for `domcontentloaded`
* try `load`
* try `networkidle` briefly
* continue even if `networkidle` never happens

---

## Notes show `null`

If notes are `null` after ingestion, that may simply mean the complexity threshold did not trigger.

You can still generate them manually using:

* the frontend buttons
* `/notes/generate`
* `/visual-notes/generate`

---

## Indexing issues with Ollama

If indexing fails while using Ollama embeddings:

1. make sure Ollama is running
2. confirm the embedding model exists

```bash
ollama list
```

If needed:

```bash
ollama pull nomic-embed-text
```



## Roadmap

### Product roadmap

* authentication and multi-user support
* browser extension ingestion
* shareable study pages
* better per-platform extraction logic
* citations in answer and note output
* export notes as markdown / PDF / slides
* background worker deployment
* usage analytics
* improved note quality and structured evaluation

### Infra roadmap

* cloud deployment guide
* ECS / Amplify / S3 / RDS production setup
* secret management
* queue workers in production
* observability dashboards
* retries and dead-letter workflows

---



## Acknowledgements

Built with:

* Next.js
* FastAPI
* SQLAlchemy
* Alembic
* pgvector
* Playwright
* LangChain
* LangGraph
* Ollama
* React Flow
* MinIO

---

## Future deployment note

Deployment is intentionally left for a later phase.

The current repo is already structured in a way that can be deployed to:

* container platforms
* managed PostgreSQL
* S3-compatible object storage
* Redis-compatible caches
* cloud-hosted model providers

A production deployment guide will be added later.

## License

Released under the MIT License.

See [LICENSE](./LICENSE) for the full text.


