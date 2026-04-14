# Architecture

## Product purpose

Chat2Study ingests a chat, user is authorized to access and transforms it into:

- raw artifacts
- normalized text
- searchable chunks
- generated notes
- visual study notes

## Planned architecture

```text
[ Next.js Web App ]
        |
        v
[ FastAPI API ]
        |
        +------> [ Redis ]
        |            |
        |            v
        |      [ Celery Workers ]
        |
        +------> [ PostgreSQL + pgvector ]
        |
        +------> [ MinIO ]
