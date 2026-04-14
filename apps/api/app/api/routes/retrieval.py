from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.retrieval import (
    AskChatRequest,
    AskChatResponse,
    RetrievedChunkResponse,
    SearchChunksRequest,
    SearchChunksResponse,
)
from app.services.qa import ChatQAService
from app.services.retrieval import ChatRetrievalService

router = APIRouter(prefix="/chats", tags=["retrieval"])


@router.post("/{chat_id}/search", response_model=SearchChunksResponse)
def search_chat(
    chat_id: UUID,
    payload: SearchChunksRequest,
    db: Session = Depends(get_db),
) -> SearchChunksResponse:
    service = ChatRetrievalService(db)

    try:
        result = service.search(chat_id, payload.query, payload.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return SearchChunksResponse(
        chat_id=result["chat_id"],
        query=result["query"],
        top_k=result["top_k"],
        matches=[RetrievedChunkResponse(**item) for item in result["matches"]],
    )


@router.post("/{chat_id}/ask", response_model=AskChatResponse)
def ask_chat(
    chat_id: UUID,
    payload: AskChatRequest,
    db: Session = Depends(get_db),
) -> AskChatResponse:
    retrieval = ChatRetrievalService(db)
    qa = ChatQAService()

    try:
        result = retrieval.search(chat_id, payload.question, payload.top_k)
        answer = qa.answer(payload.question, result["matches"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AskChatResponse(
        chat_id=result["chat_id"],
        question=payload.question,
        answer=answer["answer"],
        model_provider=answer["model_provider"],
        model_name=answer["model_name"],
        matches=[RetrievedChunkResponse(**item) for item in result["matches"]],
    )
