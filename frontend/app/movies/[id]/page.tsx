import Link from "next/link";
import { notFound } from "next/navigation";

import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";
import { fetchMovie, formatDuration } from "@/lib/catalog";

export default async function MovieDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const movieId = Number(id);

  if (!Number.isInteger(movieId) || movieId <= 0) {
    notFound();
  }

  let movie;
  try {
    movie = await fetchMovie(movieId);
  } catch {
    notFound();
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 pb-16 pt-28 sm:px-8 lg:px-10 lg:pb-24 lg:pt-32">
        <Link
          href="/movies"
          className="inline-flex w-fit items-center gap-2 text-sm font-semibold text-white/65 transition hover:text-white"
        >
          <span aria-hidden="true">←</span>
          Back to catalog
        </Link>

        <section className="grid gap-8 lg:grid-cols-[360px_minmax(0,1fr)] lg:items-start">
          <div className="overflow-hidden rounded-[2rem] border border-white/10 bg-[#101010] shadow-[0_28px_56px_rgba(0,0,0,0.28)]">
            <img src={movie.poster_url} alt={`${movie.title} poster`} className="aspect-[2/3] h-full w-full object-cover" />
          </div>

          <div className="space-y-8">
            <div className="space-y-4">
              <p className="text-xs font-semibold uppercase tracking-[0.32em] text-[#E50914]">Movie Detail</p>
              <div className="space-y-3">
                <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">{movie.title}</h1>
                <div className="flex flex-wrap items-center gap-3 text-sm text-white/60">
                  <span>{movie.release_year}</span>
                  <span className="h-1 w-1 rounded-full bg-white/25" />
                  <span>{formatDuration(movie.duration_minutes)}</span>
                  <span className="h-1 w-1 rounded-full bg-white/25" />
                  <span>{movie.language}</span>
                  <span className="h-1 w-1 rounded-full bg-white/25" />
                  <span>{movie.maturity_rating}</span>
                  <span className="h-1 w-1 rounded-full bg-white/25" />
                  <span>Rating TBD</span>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {movie.genres.map((genre) => (
                  <span
                    key={genre.id}
                    className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-white/72"
                  >
                    {genre.name}
                  </span>
                ))}
              </div>
            </div>

            <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
              <h2 className="text-lg font-semibold text-white">Synopsis</h2>
              <p className="mt-4 text-base leading-8 text-white/70">{movie.description}</p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Release year</p>
                <p className="mt-3 text-2xl font-semibold text-white">{movie.release_year}</p>
              </div>
              <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Runtime</p>
                <p className="mt-3 text-2xl font-semibold text-white">{formatDuration(movie.duration_minutes)}</p>
              </div>
              <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Language</p>
                <p className="mt-3 text-2xl font-semibold text-white">{movie.language}</p>
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <a
                href={movie.trailer_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex h-12 items-center justify-center rounded-2xl bg-[#E50914] px-6 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-[#c50b14]"
              >
                Watch Trailer
              </a>
              <Link
                href="/movies"
                className="inline-flex h-12 items-center justify-center rounded-2xl border border-white/15 px-6 text-sm font-semibold text-white/70 transition hover:border-white/35 hover:bg-white/[0.04] hover:text-white"
              >
                Explore More Movies
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
