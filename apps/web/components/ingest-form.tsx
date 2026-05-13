"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { createChat, runIngestion } from "@/lib/api";

type Stage = "idle" | "creating" | "ingesting" | "done";

const STAGE_LABELS: Record<Stage, string> = {
  idle: "Create + ingest",
  creating: "Creating record…",
  ingesting: "Ingesting chat (30–90s)…",
  done: "Done!",
};

export function IngestForm() {
  const router = useRouter();

  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [stage, setStage] = useState<Stage>("idle");
  const [error, setError] = useState<string | null>(null);

  const busy = stage !== "idle" && stage !== "done";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setStage("creating");

    try {
      const created = await createChat({
        url,
        title: title || undefined,
        source_type: "web_chat_url",
      });

      if (!created) throw new Error("Failed to create chat");

      setStage("ingesting");
      await runIngestion(created.id);
      setStage("done");
      router.push(`/chats/${created.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setStage("idle");
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg"
    >
      <h2 className="text-xl font-semibold text-slate-100">Ingest a chat</h2>
      <p className="mt-2 text-sm text-slate-400">
        Capture, index, and generate study notes from a chat URL.
      </p>

      <div className="mt-5 space-y-4">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">
            Chat URL
          </label>
          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://chatgpt.com/share/…"
            disabled={busy}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-slate-500 disabled:opacity-50"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">
            Title{" "}
            <span className="text-slate-500">(optional)</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Production RAG planning"
            disabled={busy}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-slate-500 disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={busy}
          className="inline-flex items-center gap-2 rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy && (
            <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-slate-600 border-t-slate-950" />
          )}
          {STAGE_LABELS[stage]}
        </button>

        {stage === "ingesting" && (
          <p className="text-xs text-slate-500">
            Browser capture + AI indexing in progress. Please wait…
          </p>
        )}

        {error && (
          <div className="rounded-xl border border-red-900 bg-red-950/50 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        )}
      </div>
    </form>
  );
}
