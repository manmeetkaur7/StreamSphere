"use client";

import { FormEvent, useState } from "react";

import type { MovieCardProps } from "@/components/cards/MovieCard";
import MovieRow from "@/components/home/MovieRow";
import { formatDuration, searchMoviesWithAI, type AISearchResponse, type Movie } from "@/lib/catalog";

const SUGGESTIONS = [
  { label: "Feel-Good", query: "Feel-good movies with hopeful endings" },
  { label: "Sci-Fi", query: "Thoughtful science fiction movies" },
  { label: "Date Night", query: "Romantic movies for date night" },
  { label: "Mind-Bending", query: "Mind-bending movies with a mystery" },
  { label: "Under 2 Hours", query: "Great movies under two hours" },
];

function toMovieCard(movie: Movie): MovieCardProps {
  return {
    id: movie.id,
    title: movie.title,
    year: movie.release_year,
    duration: formatDuration(movie.duration_minutes),
    rating: movie.average_rating,
    image: `url(${movie.poster_url})`,
  };
}

export default function Hero() {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<AISearchResponse | null>(null);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const prompt = query.trim();

    if (prompt.length < 3) {
      setError("Describe the kind of movie you want in at least three characters.");
      setSearchResults(null);
      return;
    }

    try {
      setSearching(true);
      setError(null);
      setSearchResults(await searchMoviesWithAI(prompt));
    } catch (requestError) {
      setSearchResults(null);
      setError(requestError instanceof Error ? requestError.message : "AI search failed. Please try again.");
    } finally {
      setSearching(false);
    }
  }

  return (
    <section id="home" className="relative overflow-hidden bg-[#070817] px-6 pb-16 pt-32 sm:px-8 sm:pb-24 lg:px-10 lg:pb-28">
      <div aria-hidden="true" className="absolute inset-0 bg-[radial-gradient(circle_at_78%_20%,rgba(126,72,255,0.22),transparent_29%),radial-gradient(circle_at_13%_82%,rgba(229,9,20,0.16),transparent_25%),linear-gradient(135deg,#070817_0%,#0b0d22_54%,#070817_100%)]" />
      <div aria-hidden="true" className="absolute inset-0 opacity-30 [background-image:linear-gradient(rgba(255,255,255,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.035)_1px,transparent_1px)] [background-size:48px_48px]" />
      <div aria-hidden="true" className="absolute right-[-7rem] top-28 h-72 w-72 rounded-full border border-fuchsia-300/10 bg-fuchsia-400/5 blur-3xl sm:h-96 sm:w-96" />

      <div className="relative mx-auto w-full max-w-7xl">
        <div className="max-w-4xl animate-[heroFade_0.8s_ease-out_both]">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#ff8b92]">AI movie discovery</p>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-[1.06] tracking-tight text-white sm:text-6xl lg:text-7xl">
            Don&apos;t search for a movie. Describe the mood.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-7 text-white/70 sm:text-lg sm:leading-8">
            Tell StreamSphere what you&apos;re in the mood for and discover movies through AI-assisted search and personalized recommendations.
          </p>
        </div>

        <div className="relative mt-10 max-w-4xl animate-[heroFade_0.8s_0.12s_ease-out_both] rounded-[1.75rem] border border-white/12 bg-[#111329]/80 p-4 shadow-[0_24px_80px_rgba(0,0,0,0.38)] backdrop-blur sm:p-5">
          <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row">
            <label className="sr-only" htmlFor="hero-ai-query">
              Describe the movie you want to watch
            </label>
            <input
              id="hero-ai-query"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              minLength={3}
              maxLength={500}
              className="h-14 min-w-0 flex-1 rounded-2xl border border-white/10 bg-black/25 px-5 text-base text-white outline-none transition placeholder:text-white/38 focus:border-[#ff7178] focus:ring-2 focus:ring-[#E50914]/35"
              placeholder="Something mysterious, emotional and futuristic, but not too scary..."
            />
            <button
              type="submit"
              disabled={searching}
              className="inline-flex h-14 shrink-0 items-center justify-center rounded-2xl bg-[#E50914] px-6 text-sm font-semibold text-white transition hover:bg-[#c50b14] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#ff8b92] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {searching ? "Discovering..." : "Discover with AI"}
            </button>
          </form>

          <div className="mt-4 flex flex-wrap gap-2" aria-label="AI search suggestions">
            {SUGGESTIONS.map((suggestion) => (
              <button
                key={suggestion.label}
                type="button"
                onClick={() => setQuery(suggestion.query)}
                className="rounded-full border border-white/12 bg-white/[0.045] px-3.5 py-2 text-sm font-medium text-white/75 transition hover:border-[#ff8b92]/60 hover:bg-white/[0.09] hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ff8b92]"
              >
                {suggestion.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6 max-w-4xl" aria-live="polite">
          {error ? <p className="rounded-xl border border-red-300/20 bg-red-400/10 px-4 py-3 text-sm text-red-100">{error}</p> : null}
          {searchResults ? (
            <div className="space-y-5">
              <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-black/20 p-4 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm leading-6 text-white/70">{searchResults.reasoning}</p>
                <span className="w-fit rounded-full border border-white/10 bg-black/30 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white/75">
                  Confidence {(searchResults.confidence * 100).toFixed(0)}%
                </span>
              </div>
              {searchResults.matching_movies.length > 0 ? (
                <MovieRow title="AI Search Results" movies={searchResults.matching_movies.map(toMovieCard)} />
              ) : (
                <p className="text-sm text-white/60">No strong matches were found for that prompt. Try a different mood or genre.</p>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
