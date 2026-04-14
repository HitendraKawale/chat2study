# Chat2Study

Chat2Study is a production-focused application that turns long AI chats into:

- preserved artifacts
- searchable RAG-ready knowledge
- smart notes
- visual study maps

## Planned stack

### Frontend

- Next.js (App Router, TypeScript)

### Backend

- FastAPI
- LangGraph
- LangChain

### Model providers

- Ollama
- OpenAI
- Anthropic
- Google Gemini

### Data and infra

- PostgreSQL + pgvector
- Redis
- MinIO (S3-compatible object storage)

### Workers

- Celery workers for ingestion, indexing, and notes generation

## Monorepo layout

```text
chat2study/
├── apps/
│   ├── web/
│   └── api/
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
└── .github/
````

## Current status

This repository is being built in phases.

### Phase 0

- monorepo initialization
- repo standards
- local infra with Postgres + pgvector, Redis, and MinIO

### Next phases

- FastAPI API skeleton
- Next.js frontend skeleton
- database models and migrations
- LangGraph ingestion pipeline
- retrieval and notes generation
- visual notes rendering
- CI/CD and release hardening

## Local development

Phase 0 local infra:

```bash
cp .env.example .env
docker compose up -d
docker compose ps
```

## License

License will be added before first public release tag.
