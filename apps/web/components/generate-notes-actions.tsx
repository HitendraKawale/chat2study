"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { generateStudyNotes, generateVisualNotes } from "@/lib/api";

type Props = {
  chatId: string;
};

export function GenerateNotesActions({ chatId }: Props) {
  const router = useRouter();
  const [busy, setBusy] = useState<"study" | "visual" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handle(type: "study" | "visual") {
    setBusy(type);
    setError(null);
    setSuccess(null);

    try {
      if (type === "study") {
        await generateStudyNotes(chatId);
        setSuccess("Study notes generated.");
      } else {
        await generateVisualNotes(chatId);
        setSuccess("Visual map generated.");
      }
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => handle("study")}
          disabled={busy !== null}
          className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 px-3.5 py-2 text-sm font-medium text-slate-100 transition hover:border-slate-500 disabled:opacity-60"
        >
          {busy === "study" && (
            <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-slate-600 border-t-slate-200" />
          )}
          {busy === "study" ? "Generating…" : "Generate study notes"}
        </button>

        <button
          type="button"
          onClick={() => handle("visual")}
          disabled={busy !== null}
          className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 px-3.5 py-2 text-sm font-medium text-slate-100 transition hover:border-slate-500 disabled:opacity-60"
        >
          {busy === "visual" && (
            <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-slate-600 border-t-slate-200" />
          )}
          {busy === "visual" ? "Generating…" : "Generate visual map"}
        </button>
      </div>

      {error && (
        <p className="text-xs text-red-400">{error}</p>
      )}
      {success && !error && (
        <p className="text-xs text-emerald-400">{success}</p>
      )}
    </div>
  );
}
