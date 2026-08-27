"use client";

export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="en">
      <body className="m-0 bg-[#050505] font-sans text-white">
        <main className="flex min-h-screen items-center justify-center px-6 text-center">
          <section className="max-w-lg rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 sm:p-12">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#ff7078]">StreamSphere</p>
            <h1 className="mt-4 text-4xl font-semibold">Something went wrong.</h1>
            <p className="mt-4 text-white/60">Refresh the experience and try again.</p>
            <button type="button" onClick={reset} className="mt-8 h-12 rounded-2xl bg-[#e50914] px-6 text-sm font-semibold text-white">Try again</button>
          </section>
        </main>
      </body>
    </html>
  );
}
