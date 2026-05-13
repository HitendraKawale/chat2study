"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { getStudyNotesDownloadUrl } from "@/lib/api";
import { getClientToken } from "@/lib/auth";
import type { StudyNoteResponse } from "@/types/api";

type Props = {
  chatId: string;
  note: StudyNoteResponse;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function StudyNotesView({ chatId, note }: Props) {
  async function handleDownload() {
    const token = getClientToken();
    const url = getStudyNotesDownloadUrl(chatId);

    const res = await fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (!res.ok) return;

    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = `study-notes-${chatId}.md`;
    a.click();
    URL.revokeObjectURL(objectUrl);
  }

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-3 text-xs text-slate-500">
          <span>Provider: {note.model_provider}</span>
          <span>Model: {note.model_name}</span>
          <span>Updated: {formatDate(note.updated_at)}</span>
        </div>
        <button
          type="button"
          onClick={handleDownload}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:border-slate-500"
        >
          Download .md
        </button>
      </div>

      <div className="prose prose-invert prose-sm max-w-none rounded-2xl border border-slate-800 bg-slate-950/60 p-5 [&_h1]:text-slate-100 [&_h2]:text-slate-100 [&_h3]:text-slate-200 [&_li]:text-slate-300 [&_p]:text-slate-300 [&_strong]:text-slate-200 [&_code]:rounded [&_code]:bg-slate-800 [&_code]:px-1 [&_code]:py-0.5 [&_code]:text-slate-200 [&_pre]:bg-slate-900 [&_pre]:border [&_pre]:border-slate-700 [&_blockquote]:border-slate-700 [&_blockquote]:text-slate-400 [&_hr]:border-slate-800 [&_a]:text-slate-300">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{note.markdown}</ReactMarkdown>
      </div>
    </div>
  );
}
