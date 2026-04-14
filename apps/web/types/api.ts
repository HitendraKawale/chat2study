export type ChatSummary = {
  id: string;
  source_id: string | null;
  title: string;
  status: string;
  url: string;
  source_type: string;
  created_at: string;
};

export type ArtifactResponse = {
  id: string;
  chat_id: string;
  artifact_type: string;
  storage_key: string;
  mime_type: string | null;
  size_bytes: number | null;
  created_at: string;
};

export type SummaryCard = {
  title: string;
  body: string;
};

export type ConceptNode = {
  id: string;
  label: string;
  kind: string;
};

export type ConceptEdge = {
  source: string;
  target: string;
  label?: string | null;
};

export type VisualNotesDocument = {
  title: string;
  summary: string;
  cards: SummaryCard[];
  nodes: ConceptNode[];
  edges: ConceptEdge[];
  suggested_questions: string[];
};

export type StudyNoteResponse = {
  id: string;
  chat_id: string;
  note_type: string;
  markdown: string;
  model_provider: string;
  model_name: string;
  created_at: string;
  updated_at: string;
};

export type VisualNoteResponse = {
  id: string;
  chat_id: string;
  note_type: string;
  document: VisualNotesDocument;
  model_provider: string;
  model_name: string;
  created_at: string;
  updated_at: string;
};

export type ChatNotesBundleResponse = {
  study_notes: StudyNoteResponse | null;
  visual_notes: VisualNoteResponse | null;
};

export type RetrievedChunkResponse = {
  chunk_id: string;
  ordinal: number;
  text: string;
  token_count: number;
  distance: number;
  metadata_json: Record<string, unknown>;
};

export type SearchChunksResponse = {
  chat_id: string;
  query: string;
  top_k: number;
  matches: RetrievedChunkResponse[];
};

export type AskChatResponse = {
  chat_id: string;
  question: string;
  answer: string;
  model_provider: string;
  model_name: string;
  matches: RetrievedChunkResponse[];
};

export type IngestionWorkflowResponse = {
  chat_id: string;
  job_id: string;
  title?: string | null;
  source_url?: string | null;
  final_url?: string | null;
  source_type?: string | null;
  source_domain?: string | null;
  selected_chat_provider?: string | null;
  selected_embedding_provider?: string | null;
  selected_chat_model?: string | null;
  selected_embedding_model?: string | null;
  capture_strategy?: string | null;
  planned_artifacts: string[];
  persisted_artifacts: {
    id: string;
    artifact_type: string;
    storage_key: string;
    mime_type?: string | null;
    size_bytes?: number | null;
  }[];
  indexed_chunk_count?: number | null;
  indexed_embedding_provider?: string | null;
  indexed_embedding_model?: string | null;
  indexed_embedding_dimensions?: number | null;
  complexity_score?: number | null;
  should_generate_notes: boolean;
  should_generate_visual_notes: boolean;
  study_note_id?: string | null;
  study_notes_generated: boolean;
  visual_note_id?: string | null;
  visual_notes_generated: boolean;
};

export type JobResponse = {
  id: string;
  chat_id: string;
  job_type: string;
  status: string;
  attempts: number;
  error_message: string | null;
  result_payload: Record<string, unknown> | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  updated_at: string;
};

export type IngestionRunResponse = {
  job: JobResponse;
  workflow: IngestionWorkflowResponse;
};
