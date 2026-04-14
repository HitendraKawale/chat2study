from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import IngestionRunResponse, IngestionWorkflowResponse, JobResponse
from app.services.job_runner import IngestionJobRunner

router = APIRouter(prefix="/chats", tags=["ingestion"])


@router.post("/{chat_id}/ingest", response_model=IngestionRunResponse)
def run_ingestion(chat_id: UUID, db: Session = Depends(get_db)) -> IngestionRunResponse:
    runner = IngestionJobRunner(db)

    try:
        job, state = runner.run(chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IngestionRunResponse(
        job=JobResponse.model_validate(job),
        workflow=IngestionWorkflowResponse(
            chat_id=state["chat_id"],
            job_id=state["job_id"],
            title=state.get("title"),
            source_url=state.get("source_url"),
            source_type=state.get("source_type"),
            source_domain=state.get("source_domain"),
            selected_chat_provider=state.get("selected_chat_provider"),
            selected_embedding_provider=state.get("selected_embedding_provider"),
            selected_chat_model=state.get("selected_chat_model"),
            selected_embedding_model=state.get("selected_embedding_model"),
            capture_strategy=state.get("capture_strategy"),
            planned_artifacts=state.get("planned_artifacts", []),
            complexity_score=state.get("complexity_score"),
            should_generate_notes=state.get("should_generate_notes", False),
            should_generate_visual_notes=state.get(
                "should_generate_visual_notes",
                False,
            ),
        ),
    )
