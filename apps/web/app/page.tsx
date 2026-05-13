import Link from "next/link";

import { IngestForm } from "@/components/ingest-form";
import { getChats } from "@/lib/api";

const STATUS_STYLES: Record<string, string> = {
  ready: "border-emerald-800 bg-emerald-950/50 text-emerald-300",
  queued: "border-slate-700 bg-slate-800/50 text-slate-400",
  planning: "border-blue-800 bg-blue-950/50 text-blue-300",
  running: "border-blue-800 bg-blue-950/50 text-blue-300",
  failed: "border-red-800 bg-red-950/50 text-red-300",
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default async function HomePage() {
  const chats = await getChats();

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-2 text-sm text-slate-400">
            Ingest a chat URL to capture, index, and generate study materials.
          </p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[400px,1fr]">
          <IngestForm />

          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Your chats</h2>
              <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400">
                {chats.length} total
              </span>
            </div>

            {chats.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-8 text-center">
                <p className="text-sm text-slate-400">No chats yet.</p>
                <p className="mt-1 text-xs text-slate-500">
                  Paste a chat URL on the left to get started.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {chats.map((chat) => (
                  <Link
                    key={chat.id}
                    href={`/chats/${chat.id}`}
                    className="group block rounded-2xl border border-slate-800 bg-slate-950/60 p-4 transition hover:border-slate-600"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="text-base font-medium text-slate-100 group-hover:text-white">
                        {chat.title}
                      </h3>
                      <span
                        className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[chat.status] ?? STATUS_STYLES.queued}`}
                      >
                        {chat.status}
                      </span>
                    </div>
                    <p className="mt-1.5 truncate text-xs text-slate-500">
                      {chat.url}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-600">
                      <span>{chat.source_type}</span>
                      <span>{formatDate(chat.created_at)}</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}
