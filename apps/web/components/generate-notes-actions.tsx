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

  async function handleStudyNotes() {
    setBusy("study");
    setError(null);

    try {
      await generateStudyNotes(chatId);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate study notes");
    } finally {
      setBusy(null);
    }
  }

  async function handleVisualNotes() {
    setBusy("visual");
    setError(null);

    try {
      await generateVisualNotes(chatId);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate visual notes");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={handleStudyNotes}
          disabled={busy !== null}
          className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-100 hover:border-slate-500 disabled:opacity-60"
        >
          {busy === "study" ? "Generating study notes..." : "Generate study notes"}
        </button>

        <button
          type="button"
          onClick={handleVisualNotes}
          disabled={busy !== null}
          className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-100 hover:border-slate-500 disabled:opacity-60"
        >
          {busy === "visual" ? "Generating visual notes..." : "Generate visual notes"}
        </button>
      </div>

      {error ? (
        <p className="mt-3 text-sm text-red-300">{error}</p>
      ) : (
        <p className="mt-3 text-sm text-slate-400">
          Use these to generate notes manually when the auto-threshold does not trigger.
        </p>
      )}
    </div>
  );
}
