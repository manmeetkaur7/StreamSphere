import Link from "next/link";

import type { Movie } from "@/lib/catalog";
import { formatDuration } from "@/lib/catalog";

interface MovieGridCardProps {
  movie: Movie;
}

export default function MovieGridCard({ movie }: MovieGridCardProps) {
  return (
    <Link
      href={`/movies/${movie.id}`}
      className="group overflow-hidden rounded-2xl border border-white/10 bg-[#101010] shadow-[0_18px_40px_rgba(0,0,0,0.28)] transition-all duration-300 hover:-translate-y-1 hover:border-white/20 hover:shadow-[0_24px_48px_rgba(229,9,20,0.18)]"
    >
      <div className="relative aspect-[2/3] overflow-hidden bg-[#191919]">
        <img
          src={movie.poster_url}
          alt={`${movie.title} poster`}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/15 to-transparent" />
        <div className="absolute left-4 right-4 top-4 flex items-start justify-between gap-3">
          <span className="rounded-full border border-white/15 bg-black/70 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-white/80 backdrop-blur-sm">
            {movie.maturity_rating}
          </span>
          <span className="rounded-full bg-[#E50914] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-white shadow-lg shadow-[#E50914]/20">
            Rating TBD
          </span>
        </div>
      </div>

      <div className="space-y-4 p-5">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2 text-xs text-white/55">
            <span>{movie.release_year}</span>
            <span className="h-1 w-1 rounded-full bg-white/25" />
            <span>{formatDuration(movie.duration_minutes)}</span>
            <span className="h-1 w-1 rounded-full bg-white/25" />
            <span>{movie.language}</span>
          </div>
          <h2 className="text-xl font-semibold tracking-tight text-white transition-colors group-hover:text-[#ffe2e3]">
            {movie.title}
          </h2>
        </div>

        <div className="flex flex-wrap gap-2">
          {movie.genres.map((genre) => (
            <span
              key={genre.id}
              className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-white/70"
            >
              {genre.name}
            </span>
          ))}
        </div>

        <p className="line-clamp-3 text-sm leading-6 text-white/64">{movie.description}</p>
      </div>
    </Link>
  );
}
