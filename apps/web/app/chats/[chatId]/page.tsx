import Link from "next/link";
import { notFound } from "next/navigation";

import { GenerateNotesActions } from "@/components/generate-notes-actions";
import { QAPanel } from "@/components/qa-panel";
import { VisualNotesGraph } from "@/components/visual-notes-graph";
import { getArtifacts, getChatById, getNotes } from "@/lib/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatBytes(value: number | null) {
  if (value === null) return "—";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export default async function ChatDetailPage({
  params,
}: {
  params: Promise<{ chatId: string }>;
}) {
  const { chatId } = await params;

  const chat = await getChatById(chatId);

  if (!chat) {
    notFound();
  }

  const [artifacts, notes] = await Promise.all([
    getArtifacts(chatId),
    getNotes(chatId),
  ]);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-8">
          <Link
            href="/"
            className="text-sm text-slate-400 transition hover:text-slate-200"
          >
            ← Back to dashboard
          </Link>

          <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight">
                {chat.title}
              </h1>
              <p className="mt-2 break-all text-sm text-slate-400">{chat.url}</p>
              <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-500">
                <span>Status: {chat.status}</span>
                <span>Created: {formatDate(chat.created_at)}</span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-300">
              <div>Chat ID</div>
              <div className="mt-1 break-all text-xs text-slate-400">
                {chat.id}
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.05fr,0.95fr]">
          <section className="space-y-6">
            <GenerateNotesActions chatId={chat.id} />

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold">Study notes</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Markdown notes generated from the indexed chat context.
                  </p>
                </div>
              </div>

              {notes.study_notes ? (
                <>
                  <div className="mb-4 flex flex-wrap gap-3 text-xs text-slate-500">
                    <span>Provider: {notes.study_notes.model_provider}</span>
                    <span>Model: {notes.study_notes.model_name}</span>
                    <span>
                      Updated: {formatDate(notes.study_notes.updated_at)}
                    </span>
                  </div>
                  <pre className="overflow-x-auto whitespace-pre-wrap rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-sm leading-6 text-slate-200">
                    {notes.study_notes.markdown}
                  </pre>
                </>
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-6 text-sm text-slate-400">
                  No study notes yet.
                </div>
              )}
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">Artifacts</h2>
              <p className="mt-1 text-sm text-slate-400">
                Stored artifact metadata from MinIO-backed ingestion.
              </p>

              <div className="mt-5 space-y-3">
                {artifacts.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-6 text-sm text-slate-400">
                    No artifacts recorded for this chat yet.
                  </div>
                ) : (
                  artifacts.map((artifact) => (
                    <div
                      key={artifact.id}
                      className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="text-sm font-medium text-slate-100">
                          {artifact.artifact_type}
                        </div>
                        <div className="text-xs text-slate-500">
                          {formatBytes(artifact.size_bytes)}
                        </div>
                      </div>
                      <div className="mt-2 break-all text-xs text-slate-400">
                        {artifact.storage_key}
                      </div>
                      <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
                        <div className="text-xs text-slate-500">
                          MIME: {artifact.mime_type ?? "unknown"}
                        </div>
                        <a
                          href={`${API_BASE_URL}/api/v1/chats/${chat.id}/artifacts/${artifact.id}/download`}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-100 hover:border-slate-500"
                        >
                          Download
                        </a>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <QAPanel chatId={chat.id} />
          </section>

          <section className="space-y-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">Visual notes</h2>
              <p className="mt-1 text-sm text-slate-400">
                Concept-map style structure for frontend rendering.
              </p>

              {notes.visual_notes ? (
                <>
                  <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                    <h3 className="text-lg font-semibold text-slate-100">
                      {notes.visual_notes.document.title}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      {notes.visual_notes.document.summary}
                    </p>
                  </div>

                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    {notes.visual_notes.document.cards.map((card) => (
                      <div
                        key={card.title}
                        className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
                      >
                        <div className="text-sm font-semibold text-slate-100">
                          {card.title}
                        </div>
                        <p className="mt-2 text-sm leading-6 text-slate-300">
                          {card.body}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4">
                    <VisualNotesGraph document={notes.visual_notes.document} />
                  </div>

                  <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                    <h4 className="text-sm font-semibold text-slate-100">
                      Suggested questions
                    </h4>
                    <ul className="mt-3 space-y-2 text-sm text-slate-300">
                      {notes.visual_notes.document.suggested_questions.map((item) => (
                        <li key={item}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                </>
              ) : (
                <div className="mt-4 rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-6 text-sm text-slate-400">
                  No visual notes yet.
                </div>
              )}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
