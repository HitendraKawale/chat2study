"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { clearAuthCookie } from "@/lib/auth";
import type { UserResponse } from "@/types/api";

type Props = {
  user: UserResponse | null;
};

export function Nav({ user }: Props) {
  const router = useRouter();

  function logout() {
    clearAuthCookie();
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <Link
          href="/"
          className="text-lg font-semibold text-slate-100 transition hover:text-white"
        >
          Chat2Study
        </Link>

        {user && (
          <div className="flex items-center gap-4">
            <span className="hidden text-sm text-slate-400 sm:block">
              {user.name ?? user.email}
            </span>
            <button
              type="button"
              onClick={logout}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-slate-500 hover:text-slate-100"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
