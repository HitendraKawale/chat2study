## Chat2Study v0.1.0

### Included
- Next.js frontend dashboard and chat detail pages
- FastAPI backend with PostgreSQL + pgvector
- Playwright chat capture pipeline
- Artifact persistence for HTML, text, screenshots, and PDFs
- Semantic retrieval and grounded Q&A
- Study notes and visual notes generation
- Visual graph rendering in the frontend
- GitHub Actions CI
- Dockerfiles for web and API

### Local evaluation metrics
Measured on a shared ChatGPT conversation using local Ollama models:

- Average ingest time: **10.666 s**
- Average indexing time: **0.407 s**
- Average semantic search latency: **0.048 s**
- Average grounded Q&A latency: **8.722 s**
- Average chunk count: **6.0**
- Artifact types captured per ingest: **4**
- Embedding setup: **768-dim nomic-embed-text**
- Chat model: **llama3.2:3b**
- Embedding provider: **Ollama**
- Chat provider: **Ollama**

### Notes
- Metrics were collected from local evaluation runs, not a production deployment.
- Local development uses MinIO for S3-compatible artifact storage.
- Deployment documentation will be added in a later release.
