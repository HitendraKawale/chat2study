from __future__ import annotations

from app.core.config import settings


class TextChunkingService:
    def __init__(self) -> None:
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    def split(self, text: str) -> list[dict]:
        normalized = text.replace("\r\n", "\n").strip()
        normalized = "\n".join(line.rstrip() for line in normalized.splitlines())

        if not normalized:
            return []

        chunks: list[dict] = []
        start = 0
        ordinal = 0

        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            chunk_text = normalized[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "ordinal": ordinal,
                        "text": chunk_text,
                        "token_count": len(chunk_text.split()),
                        "metadata_json": {
                            "start_char": start,
                            "end_char": end,
                        },
                    }
                )
                ordinal += 1

            if end >= len(normalized):
                break

            start = max(0, end - self.chunk_overlap)

        return chunks
