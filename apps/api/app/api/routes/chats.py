from urllib.parse import urlparse

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chat, Source
from app.db.session import get_db
from app.schemas.chat import ChatCreateRequest, ChatResponse

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(payload: ChatCreateRequest, db: Session = Depends(get_db)) -> ChatResponse:
    source = Source(
        source_type=payload.source_type,
        source_url=str(payload.url),
        source_domain=urlparse(str(payload.url)).netloc or None,
    )
    db.add(source)
    db.flush()

    title = payload.title or urlparse(str(payload.url)).netloc or str(payload.url)

    chat = Chat(
        source_id=source.id,
        title=title,
        status="queued",
    )
    db.add(chat)
    db.commit()
    db.refresh(source)
    db.refresh(chat)

    return ChatResponse(
        id=chat.id,
        source_id=source.id,
        title=chat.title,
        status=chat.status,
        url=source.source_url,
        source_type=source.source_type,
        created_at=chat.created_at,
    )


@router.get("", response_model=list[ChatResponse])
def list_chats(db: Session = Depends(get_db)) -> list[ChatResponse]:
    stmt = (
        select(Chat, Source)
        .join(Source, Chat.source_id == Source.id, isouter=True)
        .order_by(Chat.created_at.desc())
        .limit(50)
    )
    rows = db.execute(stmt).all()

    return [
        ChatResponse(
            id=chat.id,
            source_id=chat.source_id,
            title=chat.title,
            status=chat.status,
            url=source.source_url if source else "",
            source_type=source.source_type if source else "unknown",
            created_at=chat.created_at,
        )
        for chat, source in rows
    ]
