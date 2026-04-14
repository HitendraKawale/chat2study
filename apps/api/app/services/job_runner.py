from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Chat, Job
from app.workflows.ingestion_graph import IngestionWorkflow


class IngestionJobRunner:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run(self, chat_id: UUID) -> tuple[Job, dict]:
        chat = self.db.get(Chat, chat_id)
        if chat is None:
            raise ValueError(f"Chat not found: {chat_id}")

        job = Job(
            chat_id=chat.id,
            job_type="ingest_chat",
            status="queued",
            attempts=0,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        try:
            chat.status = "planning"
            job.status = "running"
            job.attempts += 1
            job.started_at = datetime.now(timezone.utc)
            self.db.commit()

            workflow = IngestionWorkflow(self.db)
            result = workflow.invoke(str(chat.id), str(job.id))

            chat.status = "planned"
            chat.complexity_score = result.get("complexity_score")
            job.status = "completed"
            job.finished_at = datetime.now(timezone.utc)
            job.result_payload = result.get("result_payload")
            job.error_message = None

            self.db.commit()
            self.db.refresh(chat)
            self.db.refresh(job)

            return job, result

        except Exception as exc:
            chat.status = "failed"
            job.status = "failed"
            job.finished_at = datetime.now(timezone.utc)
            job.error_message = str(exc)

            self.db.commit()
            self.db.refresh(job)
            raise
