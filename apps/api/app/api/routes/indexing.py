from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.indexing import IndexChatResponse
from app.services.indexing import ChatIndexingService

router = APIRouter(prefix="/chats", tags=["indexing"])


@router.post("/{chat_id}/index", response_model=IndexChatResponse)
def index_chat(chat_id: UUID, db: Session = Depends(get_db)) -> IndexChatResponse:
    service = ChatIndexingService(db)

    try:
        result = service.index_chat(chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IndexChatResponse(**result)
