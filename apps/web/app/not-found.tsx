import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-slate-100">
      <div className="max-w-lg rounded-3xl border border-slate-800 bg-slate-900 p-8 text-center shadow-2xl">
        <p className="text-sm uppercase tracking-[0.2em] text-slate-400">404</p>
        <h1 className="mt-3 text-3xl font-semibold">Page not found</h1>
        <p className="mt-4 text-sm leading-6 text-slate-400">
          The chat or page you requested does not exist, or it has not been created yet.
        </p>
        <Link
          href="/"
          className="mt-6 inline-flex rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-white"
        >
          Back to dashboard
        </Link>
      </div>
    </main>
  );
}
