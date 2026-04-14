from __future__ import annotations

from sqlalchemy.orm import Session

from langgraph.graph import END, START, StateGraph

from app.workflows.ingestion_nodes import IngestionNodes
from app.workflows.ingestion_state import IngestionState


class IngestionWorkflow:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.graph = self._compile()

    def _compile(self):
        nodes = IngestionNodes(self.db)

        builder = StateGraph(IngestionState)
        builder.add_node("load_chat", nodes.load_chat)
        builder.add_node("select_providers", nodes.select_providers)
        builder.add_node("plan_capture", nodes.plan_capture)
        builder.add_node("execute_capture", nodes.execute_capture)
        builder.add_node("persist_artifacts", nodes.persist_artifacts)
        builder.add_node("classify_complexity_seed", nodes.classify_complexity_seed)
        builder.add_node("build_result_payload", nodes.build_result_payload)

        builder.add_edge(START, "load_chat")
        builder.add_edge("load_chat", "select_providers")
        builder.add_edge("select_providers", "plan_capture")
        builder.add_edge("plan_capture", "execute_capture")
        builder.add_edge("execute_capture", "persist_artifacts")
        builder.add_edge("persist_artifacts", "classify_complexity_seed")
        builder.add_edge("classify_complexity_seed", "build_result_payload")
        builder.add_edge("build_result_payload", END)

        return builder.compile()

    def invoke(self, chat_id: str, job_id: str) -> IngestionState:
        return self.graph.invoke(
            {
                "chat_id": chat_id,
                "job_id": job_id,
            }
        )

