import type {
  ArtifactResponse,
  AskChatResponse,
  ChatNotesBundleResponse,
  ChatSummary,
  IngestionRunResponse,
  SearchChunksResponse,
  TokenResponse,
  UserResponse,
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getToken(): Promise<string | null> {
  if (typeof window === "undefined") {
    const { cookies } = await import("next/headers");
    const store = await cookies();
    return store.get("auth_token")?.value ?? null;
  }
  const match = document.cookie.match(/(?:^|;\s*)auth_token=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

type FetchOptions = RequestInit & {
  allowNotFound?: boolean;
  skipAuth?: boolean;
};

export async function apiFetch<T>(
  path: string,
  options: FetchOptions = {},
): Promise<T | null> {
  const { allowNotFound = false, skipAuth = false, headers, ...init } = options;

  const authHeaders: Record<string, string> = {};
  if (!skipAuth) {
    const token = await getToken();
    if (token) authHeaders["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
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

// Auth
export async function registerUser(payload: {
  email: string;
  name: string;
  password: string;
}) {
  return await apiFetch<TokenResponse>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
    skipAuth: true,
  });
}

export async function loginUser(payload: {
  email: string;
  password: string;
}) {
  return await apiFetch<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
    skipAuth: true,
  });
}

export async function getMe() {
  return await apiFetch<UserResponse>("/api/v1/auth/me", { allowNotFound: true });
}

// Chats
export async function getChats() {
  return (await apiFetch<ChatSummary[]>("/api/v1/chats")) ?? [];
}

export async function getChatById(chatId: string) {
  return await apiFetch<ChatSummary>(`/api/v1/chats/${chatId}`, {
    allowNotFound: true,
  });
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
    { method: "POST" },
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
    body: JSON.stringify({ query, top_k: topK }),
  });
}

export async function askChat(chatId: string, question: string, topK = 5) {
  return await apiFetch<AskChatResponse>(`/api/v1/chats/${chatId}/ask`, {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
}

export function getStudyNotesDownloadUrl(chatId: string) {
  return `${API_BASE_URL}/api/v1/chats/${chatId}/notes/download`;
}
