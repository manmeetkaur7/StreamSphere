"use client";

import Link from "next/link";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#050505] px-6 text-center text-white">
      <section className="max-w-lg rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-2xl shadow-black/40 sm:p-12">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#ff7078]">Connection issue</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight">We could not load this page.</h1>
        <p className="mt-4 text-base leading-7 text-white/60">The API may be restarting or temporarily unavailable. Your saved data has not been changed.</p>
        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <button type="button" onClick={reset} className="inline-flex h-12 items-center justify-center rounded-2xl bg-[#e50914] px-6 text-sm font-semibold transition hover:bg-[#c50b14]">Try again</button>
          <Link href="/" className="inline-flex h-12 items-center justify-center rounded-2xl border border-white/20 px-6 text-sm font-semibold transition hover:bg-white/10">Return home</Link>
        </div>
      </section>
    </main>
  );
}
