export default function ChatDetailLoading() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="animate-pulse space-y-6">
          <div className="h-5 w-32 rounded bg-slate-800" />
          <div className="h-10 w-80 rounded bg-slate-800" />
          <div className="grid gap-6 xl:grid-cols-[1.05fr,0.95fr]">
            <div className="space-y-6">
              <div className="h-28 rounded-2xl bg-slate-900" />
              <div className="h-80 rounded-2xl bg-slate-900" />
              <div className="h-80 rounded-2xl bg-slate-900" />
            </div>
            <div className="space-y-6">
              <div className="h-[520px] rounded-2xl bg-slate-900" />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
