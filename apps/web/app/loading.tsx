export default function Loading() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-12">
        <div className="animate-pulse space-y-6">
          <div className="h-10 w-56 rounded-xl bg-slate-800" />
          <div className="grid gap-6 xl:grid-cols-[420px,1fr]">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="h-6 w-40 rounded bg-slate-800" />
              <div className="mt-4 h-12 rounded bg-slate-800" />
              <div className="mt-3 h-12 rounded bg-slate-800" />
              <div className="mt-4 h-10 w-32 rounded bg-slate-800" />
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="h-6 w-44 rounded bg-slate-800" />
              <div className="mt-4 space-y-3">
                <div className="h-24 rounded-2xl bg-slate-800" />
                <div className="h-24 rounded-2xl bg-slate-800" />
                <div className="h-24 rounded-2xl bg-slate-800" />
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
