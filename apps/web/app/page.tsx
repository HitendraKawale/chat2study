const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const pillars = [
  {
    title: "Ingest",
    description:
      "Capture authorized chat pages, preserve HTML, screenshots, and PDFs.",
  },
  {
    title: "Retrieve",
    description:
      "Index the conversation into a searchable RAG layer with chunk-level retrieval.",
  },
  {
    title: "Study",
    description:
      "Generate text notes and visual notes for dense technical discussions.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-16">
        <div className="mb-14 flex items-center justify-between gap-6">
          <div>
            <p className="mb-3 inline-flex rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
              Production foundation · Phase 1
            </p>
            <h1 className="text-5xl font-semibold tracking-tight">
              Chat2Study
            </h1>
            <p className="mt-4 max-w-3xl text-lg text-slate-300">
              A production-focused app that turns long AI chats into preserved
              artifacts, searchable knowledge, smart notes, and visual study
              maps.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 text-sm text-slate-300 shadow-2xl">
            <p className="font-medium text-slate-100">Current API target</p>
            <p className="mt-2 break-all">{apiBaseUrl}</p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {pillars.map((pillar) => (
            <div
              key={pillar.title}
              className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg"
            >
              <h2 className="text-xl font-semibold">{pillar.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                {pillar.description}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold">Planned stack</h3>
            <ul className="mt-4 space-y-2 text-sm text-slate-300">
              <li>Next.js App Router</li>
              <li>FastAPI</li>
              <li>LangGraph + LangChain</li>
              <li>PostgreSQL + pgvector</li>
              <li>Redis + workers</li>
              <li>MinIO object storage</li>
              <li>Ollama / OpenAI / Claude / Gemini providers</li>
            </ul>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold">Next milestones</h3>
            <ul className="mt-4 space-y-2 text-sm text-slate-300">
              <li>Database models and migrations</li>
              <li>LangGraph ingestion workflow</li>
              <li>Artifact persistence</li>
              <li>RAG indexing and querying</li>
              <li>Visual notes renderer</li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
}
