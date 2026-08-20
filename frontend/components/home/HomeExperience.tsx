"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

import MovieRow from "@/components/home/MovieRow";
import type { MovieCardProps } from "@/components/cards/MovieCard";
import type { AISearchResponse, HomeResponse, Movie, RecommendationResponse } from "@/lib/catalog";
import { fetchTrendingMovies, formatDuration, searchMoviesWithAI } from "@/lib/catalog";
import { clearAccessToken, fetchWithAuth, getAccessToken } from "@/lib/auth";

function toMovieCard(movie: Movie): MovieCardProps {
  return {
    title: movie.title,
    year: movie.release_year,
    duration: formatDuration(movie.duration_minutes),
    rating: movie.average_rating,
    image: `url(${movie.poster_url})`,
  };
}

export default function HomeExperience() {
  const [authenticated, setAuthenticated] = useState(false);
  const [authResolved, setAuthResolved] = useState(false);
  const [home, setHome] = useState<HomeResponse | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [publicTrending, setPublicTrending] = useState<Movie[]>([]);
  const [query, setQuery] = useState("Funny science fiction movies from the 2020s");
  const [searchResults, setSearchResults] = useState<AISearchResponse | null>(null);
  const [loadingHome, setLoadingHome] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadData() {
      try {
        setError(null);
        setLoadingHome(true);
        const hasToken = Boolean(getAccessToken());
        if (!active) {
          return;
        }
        setAuthenticated(hasToken);
        setAuthResolved(true);

        if (hasToken) {
          const [homePayload, recommendationPayload] = await Promise.all([
            fetchWithAuth<HomeResponse>("/home"),
            fetchWithAuth<RecommendationResponse>("/recommendations"),
          ]);
          if (!active) {
            return;
          }
          setAuthenticated(true);
          setHome(homePayload);
          setRecommendations(recommendationPayload);
        } else {
          const trending = await fetchTrendingMovies();
          if (!active) {
            return;
          }
          setAuthenticated(false);
          setHome(null);
          setRecommendations(null);
          setPublicTrending(trending);
        }
      } catch (requestError) {
        if (!active) {
          return;
        }
        const message = requestError instanceof Error ? requestError.message : "Unable to load the home page.";
        if (message.includes("Could not validate credentials")) {
          clearAccessToken();
          setAuthenticated(false);
          setAuthResolved(true);
          const trending = await fetchTrendingMovies();
          if (!active) {
            return;
          }
          setHome(null);
          setRecommendations(null);
          setPublicTrending(trending);
        } else {
          setError(message);
        }
      } finally {
        if (active) {
          setAuthResolved(true);
          setLoadingHome(false);
        }
      }
    }

    void loadData();

    return () => {
      active = false;
    };
  }, []);

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      setSearching(true);
      setError(null);
      setSearchResults(await searchMoviesWithAI(query));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "AI search failed.");
    } finally {
      setSearching(false);
    }
  }

  const sections = home
    ? [
        {
          title: "Continue Watching",
          description:
            "Resume exactly where you left off. Entries are ordered by the most recently watched title.",
          movies: home.continue_watching.map((entry) => toMovieCard(entry.movie)),
        },
        {
          title: "Recommended For You",
          description:
            recommendations?.reason_for_recommendation ??
            "Personalized from your favorites, ratings, watchlist activity, and recent catalog momentum.",
          movies: home.recommended.map(toMovieCard),
        },
        {
          title: "Trending",
          description: "Ranked by favorites, watchlist adds, average rating, and review activity.",
          movies: home.trending.map(toMovieCard),
        },
        {
          title: "Favorites",
          description: "Quick access to movies you already marked as favorites.",
          movies: home.favorites.map(toMovieCard),
        },
        {
          title: "Recently Added",
          description: "New arrivals from the latest catalog additions.",
          movies: home.recently_added.map(toMovieCard),
        },
        {
          title: "Top Rated",
          description: "Highest-rated movies across the platform right now.",
          movies: home.top_rated.map(toMovieCard),
        },
      ].filter((section) => section.movies.length > 0)
    : [
        {
          title: "Trending",
          description: "Popular movies across favorites, watchlists, ratings, and reviews.",
          movies: publicTrending.map(toMovieCard),
        },
      ];

  return (
    <section id="movies" className="space-y-14 bg-black px-6 py-20 sm:px-8 lg:space-y-16 lg:px-10 lg:py-28">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-[#E50914]">
              AI discovery
            </p>
            <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Find your next favorite with personalized signals
            </h2>
            <p className="mt-3 text-base leading-7 text-white/62">
              StreamSphere now combines catalog trends, your activity, and natural-language search to surface more relevant picks.
            </p>
          </div>
          {authResolved && !authenticated ? (
            <p className="max-w-md text-sm leading-6 text-white/55">
              <Link href="/login" className="font-semibold text-white hover:text-[#ff7178]">
                Sign in
              </Link>{" "}
              to unlock recommendations, continue watching, favorites, and your personalized home feed.
            </p>
          ) : null}
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6 shadow-[0_24px_60px_rgba(0,0,0,0.28)]">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#E50914]">AI Search</p>
              <h3 className="mt-2 text-2xl font-semibold text-white">Describe what you want in plain language</h3>
              <p className="mt-3 text-sm leading-6 text-white/58">
                Search by tone, genre, time period, or viewer intent. The current provider is mock-backed and isolated behind a future-ready provider interface.
              </p>
            </div>
          </div>

          <form onSubmit={handleSearch} className="mt-6 flex flex-col gap-3 lg:flex-row">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              minLength={3}
              maxLength={500}
              className="h-12 flex-1 rounded-2xl border border-white/10 bg-white/[0.04] px-4 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/25"
              placeholder="Funny science fiction movies from the 2020s"
            />
            <button
              type="submit"
              disabled={searching}
              className="inline-flex h-12 items-center justify-center rounded-2xl bg-[#E50914] px-6 text-sm font-semibold text-white transition hover:bg-[#c50b14] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {searching ? "Searching..." : "Run AI Search"}
            </button>
          </form>

          {searchResults ? (
            <div className="mt-6 space-y-4">
              <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4 lg:flex-row lg:items-center lg:justify-between">
                <p className="text-sm leading-6 text-white/68">{searchResults.reasoning}</p>
                <span className="rounded-full border border-white/10 bg-black/40 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white/72">
                  Confidence {(searchResults.confidence * 100).toFixed(0)}%
                </span>
              </div>
              {searchResults.matching_movies.length > 0 ? (
                <MovieRow title="AI Search Results" movies={searchResults.matching_movies.map(toMovieCard)} />
              ) : (
                <p className="text-sm text-white/55">No strong matches were found for that prompt.</p>
              )}
            </div>
          ) : null}
        </div>

        {home && home.popular_genres.length > 0 ? (
          <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#E50914]">Popular Genres</p>
            <div className="mt-4 flex flex-wrap gap-3">
              {home.popular_genres.map((genre) => (
                <span
                  key={genre.id}
                  className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-medium text-white/78"
                >
                  {genre.name}
                </span>
              ))}
            </div>
            {recommendations?.recommended_genres.length ? (
              <p className="mt-4 text-sm text-white/55">
                Your strongest recommendation signals:{" "}
                {recommendations.recommended_genres.map((genre) => genre.name).join(", ")}.
              </p>
            ) : null}
          </div>
        ) : null}

        {error ? <p className="text-sm text-red-300">{error}</p> : null}

        <div className="flex flex-col gap-14 lg:gap-16">
          {loadingHome
            ? ["Recommended For You", "Trending", "Recently Added"].map((title) => (
                <MovieRow key={title} title={title} movies={[]} isLoading />
              ))
            : sections.map((section) => (
                <MovieRow
                  key={section.title}
                  title={section.title}
                  description={section.description}
                  movies={section.movies}
                />
              ))}
        </div>
      </div>
    </section>
  );
}
