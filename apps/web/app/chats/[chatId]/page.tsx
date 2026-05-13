import Link from "next/link";
import { notFound } from "next/navigation";

import { GenerateNotesActions } from "@/components/generate-notes-actions";
import { QAPanel } from "@/components/qa-panel";
import { StudyNotesView } from "@/components/study-notes-view";
import { VisualNotesGraph } from "@/components/visual-notes-graph";
import { getArtifacts, getChatById, getNotes, getStudyNotesDownloadUrl } from "@/lib/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const STATUS_STYLES: Record<string, string> = {
  ready: "border-emerald-800 bg-emerald-950/50 text-emerald-300",
  queued: "border-slate-700 bg-slate-800/50 text-slate-400",
  planning: "border-blue-800 bg-blue-950/50 text-blue-300",
  running: "border-blue-800 bg-blue-950/50 text-blue-300",
  failed: "border-red-800 bg-red-950/50 text-red-300",
};

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
  if (!chat) notFound();

  const [artifacts, notes] = await Promise.all([
    getArtifacts(chatId),
    getNotes(chatId),
  ]);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-8">
        {/* Header */}
        <div className="mb-6">
          <Link
            href="/"
            className="text-sm text-slate-500 transition hover:text-slate-300"
          >
            ← Dashboard
          </Link>
          <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-semibold tracking-tight truncate">
                  {chat.title}
                </h1>
                <span
                  className={`shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[chat.status] ?? STATUS_STYLES.queued}`}
                >
                  {chat.status}
                </span>
              </div>
              <p className="mt-1.5 truncate text-sm text-slate-400">{chat.url}</p>
            </div>

            <GenerateNotesActions chatId={chat.id} />
          </div>
        </div>

        {/* Two-column layout */}
        <div className="grid gap-6 xl:grid-cols-2">
          {/* Left: Study notes + Q&A */}
          <div className="space-y-6">
            {/* Study notes */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="mb-4 text-lg font-semibold">Study Notes</h2>
              {notes.study_notes ? (
                <StudyNotesView chatId={chat.id} note={notes.study_notes} />
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-6 text-center">
                  <p className="text-sm text-slate-400">No study notes yet.</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Use the Generate buttons above to create them.
                  </p>
                </div>
              )}
            </section>

            {/* Q&A */}
            <QAPanel chatId={chat.id} />
          </div>

          {/* Right: Visual map + Artifacts */}
          <div className="space-y-6">
            {/* Visual notes */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="mb-4 text-lg font-semibold">Visual Map</h2>

              {notes.visual_notes ? (
                <div className="space-y-4">
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                    <h3 className="font-semibold text-slate-100">
                      {notes.visual_notes.document.title}
                    </h3>
                    <p className="mt-1.5 text-sm leading-6 text-slate-300">
                      {notes.visual_notes.document.summary}
                    </p>
                  </div>

                  <VisualNotesGraph document={notes.visual_notes.document} />

                  {notes.visual_notes.document.cards.length > 0 && (
                    <div className="grid gap-3 sm:grid-cols-2">
                      {notes.visual_notes.document.cards.map((card) => (
                        <div
                          key={card.title}
                          className="rounded-xl border border-slate-800 bg-slate-950/60 p-4"
                        >
                          <div className="text-sm font-semibold text-slate-100">
                            {card.title}
                          </div>
                          <p className="mt-1.5 text-sm leading-5 text-slate-400">
                            {card.body}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  {notes.visual_notes.document.suggested_questions.length > 0 && (
                    <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                      <h4 className="mb-3 text-sm font-semibold text-slate-200">
                        Suggested questions
                      </h4>
                      <ul className="space-y-2">
                        {notes.visual_notes.document.suggested_questions.map((q) => (
                          <li key={q} className="flex gap-2 text-sm text-slate-400">
                            <span className="mt-0.5 text-slate-600">→</span>
                            {q}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-6 text-center">
                  <p className="text-sm text-slate-400">No visual map yet.</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Use the Generate buttons above to create one.
                  </p>
                </div>
              )}
            </section>

            {/* Artifacts */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="mb-4 text-lg font-semibold">Artifacts</h2>
              {artifacts.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-6 text-center text-sm text-slate-400">
                  No artifacts recorded.
                </div>
              ) : (
                <div className="space-y-3">
                  {artifacts.map((artifact) => (
                    <div
                      key={artifact.id}
                      className="rounded-xl border border-slate-800 bg-slate-950/60 p-4"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <span className="text-sm font-medium text-slate-200">
                            {artifact.artifact_type}
                          </span>
                          <span className="ml-2 text-xs text-slate-500">
                            {formatBytes(artifact.size_bytes)}
                          </span>
                        </div>
                        <a
                          href={`${API_BASE_URL}/api/v1/chats/${chat.id}/artifacts/${artifact.id}/download`}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-lg border border-slate-700 px-3 py-1 text-xs font-medium text-slate-200 transition hover:border-slate-500"
                        >
                          Download
                        </a>
                      </div>
                      <p className="mt-1.5 truncate text-xs text-slate-500">
                        {artifact.mime_type ?? "unknown"} · {artifact.storage_key}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>
      </section>
    </main>
  );
}
