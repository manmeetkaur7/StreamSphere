"use client";

import { FormEvent, useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";

import { clearAccessToken, fetchWithAuth, getAccessToken, resolveApiBaseUrl } from "@/lib/auth";
import type { FavoriteItem, Movie, Review, WatchlistItem } from "@/lib/catalog";
import { fetchMovie, formatDuration } from "@/lib/catalog";

interface MovieEngagementClientProps {
  initialMovie: Movie;
}

export default function MovieEngagementClient({ initialMovie }: MovieEngagementClientProps) {
  const [movie, setMovie] = useState(initialMovie);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [watchlisted, setWatchlisted] = useState(false);
  const [favorited, setFavorited] = useState(false);
  const [ratingValue, setRatingValue] = useState("5");
  const [reviewTitle, setReviewTitle] = useState("");
  const [reviewBody, setReviewBody] = useState("");
  const [reviewRating, setReviewRating] = useState("5");
  const [loadingReviews, setLoadingReviews] = useState(true);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [authResolved, setAuthResolved] = useState(false);

  async function refreshMovie() {
    setMovie(await fetchMovie(movie.id));
  }

  async function fetchReviewsData(movieId: number) {
    const response = await fetch(`${resolveApiBaseUrl()}/movies/${movieId}/reviews`, { cache: "no-store" });
    return (await response.json()) as Review[];
  }

  async function refreshReviews() {
    setLoadingReviews(true);
    try {
      setReviews(await fetchReviewsData(movie.id));
    } finally {
      setLoadingReviews(false);
    }
  }

  async function fetchSavedStateData(movieId: number) {
    const [watchlist, favorites] = await Promise.all([
      fetchWithAuth<WatchlistItem[]>("/watchlist"),
      fetchWithAuth<FavoriteItem[]>("/favorites"),
    ]);
    return {
      watchlisted: watchlist.some((item) => item.movie.id === movieId),
      favorited: favorites.some((item) => item.movie.id === movieId),
    };
  }

  useEffect(() => {
    let active = true;

    async function loadEngagement() {
      const hasToken = Boolean(getAccessToken());
      if (!active) {
        return;
      }

      setAuthenticated(hasToken);
      setAuthResolved(true);

      try {
        const reviewsPayload = await fetchReviewsData(movie.id);
        if (!active) {
          return;
        }
        setReviews(reviewsPayload);
      } finally {
        if (active) {
          setLoadingReviews(false);
        }
      }

      if (!hasToken) {
        if (!active) {
          return;
        }
        setWatchlisted(false);
        setFavorited(false);
        return;
      }

      try {
        const { watchlisted: nextWatchlisted, favorited: nextFavorited } = await fetchSavedStateData(movie.id);
        if (!active) {
          return;
        }
        setWatchlisted(nextWatchlisted);
        setFavorited(nextFavorited);
      } catch (requestError) {
        if (!active) {
          return;
        }
        setError(requestError instanceof Error ? requestError.message : "Unable to load saved items.");
      }
    }

    void loadEngagement();

    return () => {
      active = false;
    };
  }, [movie.id]);

  async function handleAction(action: string, callback: () => Promise<void>) {
    if (!getAccessToken()) {
      setError("Please sign in to use this feature.");
      return;
    }

    try {
      setBusyAction(action);
      setError(null);
      setFeedback(null);
      await callback();
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Action failed.";
      if (message.includes("Could not validate credentials")) {
        clearAccessToken();
        setAuthenticated(false);
        setWatchlisted(false);
        setFavorited(false);
      }
      setError(message);
    } finally {
      setBusyAction(null);
    }
  }

  async function toggleWatchlist() {
    await handleAction("watchlist", async () => {
      if (watchlisted) {
        await fetchWithAuth(`/watchlist/${movie.id}`, { method: "DELETE" });
        setWatchlisted(false);
        setFeedback("Removed from watchlist.");
      } else {
        await fetchWithAuth(`/watchlist/${movie.id}`, { method: "POST" });
        setWatchlisted(true);
        setFeedback("Added to watchlist.");
      }
    });
  }

  async function toggleFavorite() {
    await handleAction("favorite", async () => {
      if (favorited) {
        await fetchWithAuth(`/favorites/${movie.id}`, { method: "DELETE" });
        setFavorited(false);
        setFeedback("Removed from favorites.");
      } else {
        await fetchWithAuth(`/favorites/${movie.id}`, { method: "POST" });
        setFavorited(true);
        setFeedback("Added to favorites.");
      }
    });
  }

  async function submitRating(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await handleAction("rating", async () => {
      const body = JSON.stringify({ rating: Number(ratingValue) });
      try {
        await fetchWithAuth(`/movies/${movie.id}/rating`, { method: "POST", body });
      } catch (requestError) {
        if (requestError instanceof Error && requestError.message.includes("already rated")) {
          await fetchWithAuth(`/movies/${movie.id}/rating`, { method: "PUT", body });
        } else {
          throw requestError;
        }
      }

      await refreshMovie();
      setFeedback("Your rating was saved.");
    });
  }

  async function submitReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await handleAction("review", async () => {
      await fetchWithAuth(`/movies/${movie.id}/reviews`, {
        method: "POST",
        body: JSON.stringify({
          title: reviewTitle,
          body: reviewBody,
          rating: Number(reviewRating),
        }),
      });
      setReviewTitle("");
      setReviewBody("");
      setReviewRating("5");
      await Promise.all([refreshMovie(), refreshReviews()]);
      setFeedback("Your review was published.");
    });
  }

  return (
    <section className="grid gap-8 lg:grid-cols-[360px_minmax(0,1fr)] lg:items-start">
      <div className="overflow-hidden rounded-[2rem] border border-white/10 bg-[#101010] shadow-[0_28px_56px_rgba(0,0,0,0.28)]">
        <div className="relative aspect-[2/3]">
          <Image
            src={movie.poster_url}
            alt={`${movie.title} poster`}
            fill
            sizes="(min-width: 1024px) 360px, 100vw"
            className="object-cover"
          />
        </div>
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
              <span>{movie.average_rating.toFixed(1)} avg</span>
              <span className="h-1 w-1 rounded-full bg-white/25" />
              <span>{movie.review_count} reviews</span>
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

        <div className="grid gap-4 sm:grid-cols-4">
          <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Average rating</p>
            <p className="mt-3 text-2xl font-semibold text-white">{movie.average_rating.toFixed(1)}</p>
          </div>
          <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Ratings</p>
            <p className="mt-3 text-2xl font-semibold text-white">{movie.total_ratings}</p>
          </div>
          <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Reviews</p>
            <p className="mt-3 text-2xl font-semibold text-white">{movie.review_count}</p>
          </div>
          <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Runtime</p>
            <p className="mt-3 text-2xl font-semibold text-white">{formatDuration(movie.duration_minutes)}</p>
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
          <button type="button" onClick={() => void toggleWatchlist()} disabled={busyAction === "watchlist"} className="inline-flex h-12 items-center justify-center rounded-2xl border border-white/15 px-6 text-sm font-semibold text-white/80 transition hover:border-white/35 hover:bg-white/[0.04] hover:text-white disabled:cursor-not-allowed disabled:opacity-60">
            {watchlisted ? "Remove from Watchlist" : "Add to Watchlist"}
          </button>
          <button type="button" onClick={() => void toggleFavorite()} disabled={busyAction === "favorite"} className="inline-flex h-12 items-center justify-center rounded-2xl border border-white/15 px-6 text-sm font-semibold text-white/80 transition hover:border-white/35 hover:bg-white/[0.04] hover:text-white disabled:cursor-not-allowed disabled:opacity-60">
            {favorited ? "Unfavorite" : "Favorite"}
          </button>
        </div>

        {authResolved && !authenticated && (
          <p className="text-sm text-white/55">
            <Link href="/login" className="font-semibold text-white hover:text-[#ff7178]">Sign in</Link> to manage your watchlist, favorites, ratings, and reviews.
          </p>
        )}
        {feedback && <p className="text-sm text-emerald-300">{feedback}</p>}
        {error && <p className="text-sm text-red-300">{error}</p>}

        <div className="grid gap-6 xl:grid-cols-2">
          <form onSubmit={submitRating} className="rounded-[2rem] border border-white/10 bg-[#101010] p-6">
            <h2 className="text-lg font-semibold text-white">Rate Movie</h2>
            <p className="mt-2 text-sm leading-6 text-white/55">Submit a score from 1 to 5. If you already rated this movie, saving again updates it.</p>
            <div className="mt-5 flex flex-col gap-3 sm:flex-row">
              <select value={ratingValue} onChange={(event) => setRatingValue(event.target.value)} className="h-11 rounded-xl border border-white/10 bg-white/[0.04] px-3 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30">
                {[1, 2, 3, 4, 5].map((value) => (
                  <option key={value} value={value}>{value} star{value === 1 ? "" : "s"}</option>
                ))}
              </select>
              <button type="submit" disabled={busyAction === "rating"} className="inline-flex h-11 items-center justify-center rounded-xl bg-[#E50914] px-5 text-sm font-semibold text-white transition hover:bg-[#c50b14] disabled:cursor-not-allowed disabled:opacity-60">
                {busyAction === "rating" ? "Saving..." : "Save Rating"}
              </button>
            </div>
          </form>

          <form onSubmit={submitReview} className="rounded-[2rem] border border-white/10 bg-[#101010] p-6">
            <h2 className="text-lg font-semibold text-white">Write Review</h2>
            <div className="mt-5 space-y-3">
              <input value={reviewTitle} onChange={(event) => setReviewTitle(event.target.value)} required minLength={1} maxLength={255} placeholder="Review title" className="h-11 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30" />
              <textarea value={reviewBody} onChange={(event) => setReviewBody(event.target.value)} required minLength={10} rows={5} placeholder="Share what stood out to you." className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30" />
              <div className="flex flex-col gap-3 sm:flex-row">
                <select value={reviewRating} onChange={(event) => setReviewRating(event.target.value)} className="h-11 rounded-xl border border-white/10 bg-white/[0.04] px-3 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30">
                  {[1, 2, 3, 4, 5].map((value) => (
                    <option key={value} value={value}>{value} star{value === 1 ? "" : "s"}</option>
                  ))}
                </select>
                <button type="submit" disabled={busyAction === "review"} className="inline-flex h-11 items-center justify-center rounded-xl bg-[#E50914] px-5 text-sm font-semibold text-white transition hover:bg-[#c50b14] disabled:cursor-not-allowed disabled:opacity-60">
                  {busyAction === "review" ? "Publishing..." : "Publish Review"}
                </button>
              </div>
            </div>
          </form>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-white">Reviews</h2>
              <p className="mt-2 text-sm text-white/55">See what other viewers thought about this movie.</p>
            </div>
            <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-white/65">
              {movie.review_count} total
            </span>
          </div>
          <div className="mt-6 space-y-4">
            {loadingReviews ? (
              <p className="text-sm text-white/55">Loading reviews...</p>
            ) : reviews.length === 0 ? (
              <p className="text-sm text-white/55">No reviews yet. Be the first to write one.</p>
            ) : (
              reviews.map((review) => (
                <article key={review.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <h3 className="text-base font-semibold text-white">{review.title}</h3>
                      <p className="mt-1 text-sm text-white/45">by {review.username}</p>
                    </div>
                    <span className="rounded-full bg-[#E50914]/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-[#ff9fa4]">
                      {review.rating}/5
                    </span>
                  </div>
                  <p className="mt-4 text-sm leading-7 text-white/65">{review.body}</p>
                </article>
              ))
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
