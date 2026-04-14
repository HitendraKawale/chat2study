import Link from "next/link";

import { IngestForm } from "@/components/ingest-form";
import { getChats } from "@/lib/api";

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
      <section className="mx-auto max-w-7xl px-6 py-12">
        <div className="mb-10 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="mb-3 inline-flex rounded-full border border-slate-800 px-3 py-1 text-xs text-slate-300">
              Phase 7 · Frontend integration
            </p>
            <h1 className="text-4xl font-semibold tracking-tight">Chat2Study</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
              Ingest long AI chats, preserve artifacts, index them for retrieval,
              and turn them into study notes and visual maps.
            </p>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px,1fr]">
          <IngestForm />

          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Recent chats</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Latest captured conversations from your local backend.
                </p>
              </div>
              <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
                {chats.length} total
              </span>
            </div>

            {chats.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-8 text-sm text-slate-400">
                No chats yet. Ingest one using the form on the left.
              </div>
            ) : (
              <div className="space-y-4">
                {chats.map((chat) => (
                  <Link
                    key={chat.id}
                    href={`/chats/${chat.id}`}
                    className="block rounded-2xl border border-slate-800 bg-slate-950/60 p-5 transition hover:border-slate-600"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <h3 className="text-lg font-medium text-slate-100">
                        {chat.title}
                      </h3>
                      <span className="rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-300">
                        {chat.status}
                      </span>
                    </div>

                    <p className="mt-2 break-all text-sm text-slate-400">
                      {chat.url}
                    </p>

                    <div className="mt-4 flex flex-wrap gap-3 text-xs text-slate-500">
                      <span>Type: {chat.source_type}</span>
                      <span>Created: {formatDate(chat.created_at)}</span>
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
