import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#050505] px-6 text-center text-white">
      <section className="max-w-lg rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-2xl shadow-black/40 sm:p-12">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#ff7078]">404</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight">This story is not in the catalog.</h1>
        <p className="mt-4 text-base leading-7 text-white/60">The page may have moved, or the movie is no longer available in this StreamSphere environment.</p>
        <Link href="/movies" className="mt-8 inline-flex h-12 items-center justify-center rounded-2xl bg-[#e50914] px-6 text-sm font-semibold transition hover:bg-[#c50b14]">
          Browse movies
        </Link>
      </section>
    </main>
  );
}
