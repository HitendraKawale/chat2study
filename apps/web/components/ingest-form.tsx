"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { createChat, runIngestion } from "@/lib/api";

export function IngestForm() {
  const router = useRouter();

  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const created = await createChat({
        url,
        title: title || undefined,
        source_type: "web_chat_url",
      });

      if (!created) {
        throw new Error("Failed to create chat");
      }

      await runIngestion(created.id);
      router.push(`/chats/${created.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg"
    >
      <h2 className="text-xl font-semibold text-slate-100">Ingest a chat</h2>
      <p className="mt-2 text-sm text-slate-400">
        Create a chat record and immediately run the ingestion workflow.
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
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://chatgpt.com/share/..."
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none ring-0 placeholder:text-slate-500 focus:border-slate-500"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">
            Optional title
          </label>
          <input
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Production RAG planning chat"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none ring-0 placeholder:text-slate-500 focus:border-slate-500"
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? "Creating and ingesting..." : "Create + ingest"}
        </button>

        {error ? (
          <div className="rounded-xl border border-red-900 bg-red-950/50 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}
      </div>
    </form>
  );
}
