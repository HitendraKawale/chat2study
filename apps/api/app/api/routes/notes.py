from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.notes import (
    ChatNotesBundleResponse,
    StudyNoteResponse,
    VisualNoteResponse,
    VisualNotesDocument,
)
from app.services.notes import ChatNotesService

router = APIRouter(prefix="/chats", tags=["notes"])


def _build_bundle(service: ChatNotesService, chat_id: UUID) -> ChatNotesBundleResponse:
    bundle = service.get_notes_bundle(chat_id)

    study = bundle["study_notes"]
    visual = bundle["visual_notes"]

    return ChatNotesBundleResponse(
        study_notes=(
            StudyNoteResponse(
                id=study.id,
                chat_id=study.chat_id,
                note_type=study.note_type,
                markdown=study.content_md or "",
                model_provider=study.model_provider,
                model_name=study.model_name,
                created_at=study.created_at,
                updated_at=study.updated_at,
            )
            if study
            else None
        ),
        visual_notes=(
            VisualNoteResponse(
                id=visual.id,
                chat_id=visual.chat_id,
                note_type=visual.note_type,
                document=VisualNotesDocument.model_validate(visual.content_json or {}),
                model_provider=visual.model_provider,
                model_name=visual.model_name,
                created_at=visual.created_at,
                updated_at=visual.updated_at,
            )
            if visual
            else None
        ),
    )


@router.get("/{chat_id}/notes", response_model=ChatNotesBundleResponse)
def get_chat_notes(chat_id: UUID, db: Session = Depends(get_db)) -> ChatNotesBundleResponse:
    service = ChatNotesService(db)
    return _build_bundle(service, chat_id)


@router.post("/{chat_id}/notes/generate", response_model=StudyNoteResponse)
def generate_study_notes(chat_id: UUID, db: Session = Depends(get_db)) -> StudyNoteResponse:
    service = ChatNotesService(db)

    try:
        note = service.generate_study_notes(chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return StudyNoteResponse(
        id=note.id,
        chat_id=note.chat_id,
        note_type=note.note_type,
        markdown=note.content_md or "",
        model_provider=note.model_provider,
        model_name=note.model_name,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.post("/{chat_id}/visual-notes/generate", response_model=VisualNoteResponse)
def generate_visual_notes(chat_id: UUID, db: Session = Depends(get_db)) -> VisualNoteResponse:
    service = ChatNotesService(db)

    try:
        note = service.generate_visual_notes(chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return VisualNoteResponse(
        id=note.id,
        chat_id=note.chat_id,
        note_type=note.note_type,
        document=VisualNotesDocument.model_validate(note.content_json or {}),
        model_provider=note.model_provider,
        model_name=note.model_name,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )
