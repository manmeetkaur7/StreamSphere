"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import MovieRow from "@/components/home/MovieRow";
import type { MovieCardProps } from "@/components/cards/MovieCard";
import type { HomeResponse, Movie, RecommendationResponse } from "@/lib/catalog";
import { fetchTrendingMovies, formatDuration } from "@/lib/catalog";
import { clearAccessToken, fetchWithAuth, getAccessToken } from "@/lib/auth";

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

export default function HomeExperience() {
  const [authenticated, setAuthenticated] = useState(false);
  const [authResolved, setAuthResolved] = useState(false);
  const [home, setHome] = useState<HomeResponse | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [publicTrending, setPublicTrending] = useState<Movie[]>([]);
  const [loadingHome, setLoadingHome] = useState(true);
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

  const primarySections = home
    ? [
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
          title: "Continue Watching",
          description:
            "Resume exactly where you left off. Entries are ordered by the most recently watched title.",
          movies: home.continue_watching.map((entry) => toMovieCard(entry.movie)),
        },
      ].filter((section) => section.movies.length > 0)
    : [
        {
          title: "Trending",
          description: "Popular movies across favorites, watchlists, ratings, and reviews.",
          movies: publicTrending.map(toMovieCard),
        },
      ];

  const additionalSections = home
    ? [
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
    : [];

  return (
    <section id="movies" className="space-y-14 bg-black px-6 py-20 sm:px-8 lg:space-y-16 lg:px-10 lg:py-28">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-14 lg:gap-16">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[#ff8b92]">Your home feed</p>
            <p className="mt-3 text-base leading-7 text-white/62">
              Recommendations and trending titles update from your activity and the catalog.
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

        <div className="flex flex-col gap-14 lg:gap-16">
          {loadingHome
            ? ["Recommended For You", "Trending", "Continue Watching"].map((title) => (
                <MovieRow key={title} title={title} movies={[]} isLoading />
              ))
            : primarySections.map((section) => (
                <MovieRow
                  key={section.title}
                  title={section.title}
                  description={section.description}
                  movies={section.movies}
                />
              ))}
        </div>

        {home && home.popular_genres.length > 0 ? (
          <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#ff8b92]">Browse by Genre</p>
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
          {!loadingHome && additionalSections.map((section) => (
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
