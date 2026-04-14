import type {
  ArtifactResponse,
  AskChatResponse,
  ChatNotesBundleResponse,
  ChatSummary,
  IngestionRunResponse,
  SearchChunksResponse,
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type FetchOptions = RequestInit & {
  allowNotFound?: boolean;
};

export async function apiFetch<T>(
  path: string,
  options: FetchOptions = {},
): Promise<T | null> {
  const { allowNotFound = false, headers, ...init } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(headers ?? {}),
    },
    cache: "no-store",
  });

  if (allowNotFound && response.status === 404) {
    return null;
  }

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `API request failed (${response.status}) ${path}: ${text || response.statusText}`,
    );
  }

  return (await response.json()) as T;
}

export async function getChats() {
  return (await apiFetch<ChatSummary[]>("/api/v1/chats")) ?? [];
}

export async function getChatById(chatId: string) {
  const chats = await getChats();
  return chats.find((chat) => chat.id === chatId) ?? null;
}

export async function getArtifacts(chatId: string) {
  return (
    (await apiFetch<ArtifactResponse[]>(
      `/api/v1/chats/${chatId}/artifacts`,
      { allowNotFound: true },
    )) ?? []
  );
}

export async function getNotes(chatId: string) {
  return (
    (await apiFetch<ChatNotesBundleResponse>(
      `/api/v1/chats/${chatId}/notes`,
      { allowNotFound: true },
    )) ?? {
      study_notes: null,
      visual_notes: null,
    }
  );
}

export async function createChat(payload: {
  url: string;
  title?: string;
  source_type?: string;
}) {
  return await apiFetch<ChatSummary>("/api/v1/chats", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function runIngestion(chatId: string) {
  return await apiFetch<IngestionRunResponse>(
    `/api/v1/chats/${chatId}/ingest`,
    {
      method: "POST",
    },
  );
}

export async function generateStudyNotes(chatId: string) {
  return await apiFetch(`/api/v1/chats/${chatId}/notes/generate`, {
    method: "POST",
  });
}

export async function generateVisualNotes(chatId: string) {
  return await apiFetch(`/api/v1/chats/${chatId}/visual-notes/generate`, {
    method: "POST",
  });
}

export async function searchChat(chatId: string, query: string, topK = 5) {
  return await apiFetch<SearchChunksResponse>(`/api/v1/chats/${chatId}/search`, {
    method: "POST",
    body: JSON.stringify({
      query,
      top_k: topK,
    }),
  });
}

export async function askChat(chatId: string, question: string, topK = 5) {
  return await apiFetch<AskChatResponse>(`/api/v1/chats/${chatId}/ask`, {
    method: "POST",
    body: JSON.stringify({
      question,
      top_k: topK,
    }),
  });
}
