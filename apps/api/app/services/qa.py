from __future__ import annotations

from typing import Any

from app.services.providers import ProviderFactory


def _coerce_content(value: Any) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()

    return str(value)


class ChatQAService:
    def answer(self, question: str, matches: list[dict]) -> dict[str, Any]:
        provider = ProviderFactory.default_chat_provider()
        model_name = ProviderFactory.resolve_chat_model_name(provider)
        model = ProviderFactory.get_chat_model(provider)

        context_blocks = []
        for item in matches:
            context_blocks.append(
                f"[chunk ordinal={item['ordinal']} distance={item['distance']:.6f}]\n{item['text']}"
            )

        prompt = f"""
You are answering a question about an indexed chat.

Rules:
- Use only the retrieved context below.
- If the answer is not supported by the context, say that clearly.
- Be concise and practical.
- Do not invent facts.

Question:
{question}

Retrieved context:
{chr(10).join(context_blocks)}
""".strip()

        response = model.invoke(prompt)
        answer_text = _coerce_content(response.content)

        return {
            "model_provider": provider,
            "model_name": model_name,
            "answer": answer_text,
        }
