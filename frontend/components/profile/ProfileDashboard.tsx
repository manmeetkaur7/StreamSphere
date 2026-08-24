"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";

import { clearAccessToken, fetchWithAuth, getAccessToken } from "@/lib/auth";
import type { Profile, ProfileInsights } from "@/lib/catalog";
import { formatDuration, formatRelativeTimestamp } from "@/lib/catalog";

function formatEventLabel(eventType: string) {
  return eventType.replaceAll("_", " ");
}

export default function ProfileDashboard() {
  const [authenticated, setAuthenticated] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [insights, setInsights] = useState<ProfileInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadProfile() {
      const hasToken = Boolean(getAccessToken());
      if (!active) {
        return;
      }

      setAuthenticated(hasToken);

      if (!hasToken) {
        setLoading(false);
        setError("Please sign in to view your profile.");
        return;
      }

      try {
        const [profilePayload, insightsPayload] = await Promise.all([
          fetchWithAuth<Profile>("/profile"),
          fetchWithAuth<ProfileInsights>("/profile/insights"),
        ]);
        if (!active) {
          return;
        }
        setProfile(profilePayload);
        setInsights(insightsPayload);
        setError(null);
      } catch (requestError) {
        if (!active) {
          return;
        }

        const message = requestError instanceof Error ? requestError.message : "Unable to load your profile.";
        if (message.includes("Could not validate credentials")) {
          clearAccessToken();
          setAuthenticated(false);
          setError("Please sign in to view your profile.");
        } else {
          setError(message);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadProfile();

    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return <p className="text-sm text-white/60">Loading your profile...</p>;
  }

  if (!authenticated || !profile || !insights) {
    return (
      <div className="rounded-[2rem] border border-dashed border-white/12 bg-[#0d0d0d] p-8 text-center">
        <h2 className="text-2xl font-semibold text-white">Profile unavailable</h2>
        <p className="mt-3 text-sm leading-6 text-white/60">{error ?? "Please sign in to continue."}</p>
        <Link href="/login" className="mt-6 inline-flex h-12 items-center justify-center rounded-2xl bg-[#E50914] px-6 text-sm font-semibold text-white transition hover:bg-[#c50b14]">
          Go to Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5 xl:col-span-2">
          <div className="flex flex-wrap items-center gap-3">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Account</p>
            {profile.is_admin ? (
              <span className="rounded-full border border-[#E50914]/30 bg-[#E50914]/12 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#ff9fa4]">
                Admin
              </span>
            ) : null}
          </div>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">{profile.username}</h1>
          <p className="mt-2 text-sm text-white/55">{profile.email}</p>
          <p className="mt-4 text-sm text-white/45">
            Member since {new Date(profile.account_creation_date).toLocaleDateString()}
          </p>
          {profile.is_admin ? (
            <Link href="/admin" className="mt-5 inline-flex rounded-full border border-white/15 px-4 py-2 text-sm font-medium text-white/80 transition hover:border-white/30 hover:text-white">
              Open admin dashboard
            </Link>
          ) : null}
        </div>
        <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Favorites</p>
          <p className="mt-3 text-3xl font-semibold text-white">{profile.favorite_count}</p>
        </div>
        <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Watchlist</p>
          <p className="mt-3 text-3xl font-semibold text-white">{profile.watchlist_count}</p>
        </div>
        <div className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Average rating</p>
          <p className="mt-3 text-3xl font-semibold text-white">{profile.average_rating_given.toFixed(1)}</p>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-white">Insights</h2>
              <p className="mt-2 text-sm text-white/55">Your favorite genres, completion habits, and recent activity.</p>
            </div>
            <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-white/65">
              {insights.movies_completed} completed
            </span>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-white/40">In Progress</p>
              <p className="mt-2 text-2xl font-semibold text-white">{insights.movies_in_progress}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-white/40">Watchlist Entries</p>
              <p className="mt-2 text-2xl font-semibold text-white">{insights.total_watchlist_entries}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-white/40">Reviews</p>
              <p className="mt-2 text-2xl font-semibold text-white">{insights.total_reviews}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-white/40">Avg Rating Given</p>
              <p className="mt-2 text-2xl font-semibold text-white">{insights.average_rating_given.toFixed(1)}</p>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <h3 className="text-sm font-semibold text-white">Favorite Genres</h3>
              <div className="mt-4 flex flex-wrap gap-2">
                {insights.favorite_genres.length === 0 ? (
                  <p className="text-sm text-white/50">No favorite patterns yet.</p>
                ) : (
                  insights.favorite_genres.map((genre) => (
                    <span key={genre.name} className="rounded-full border border-white/10 px-3 py-1 text-xs text-white/70">
                      {genre.name} · {genre.count}
                    </span>
                  ))
                )}
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <h3 className="text-sm font-semibold text-white">Most Viewed Genres</h3>
              <div className="mt-4 flex flex-wrap gap-2">
                {insights.most_viewed_genres.length === 0 ? (
                  <p className="text-sm text-white/50">View a few movies to unlock this section.</p>
                ) : (
                  insights.most_viewed_genres.map((genre) => (
                    <span key={genre.name} className="rounded-full border border-white/10 px-3 py-1 text-xs text-white/70">
                      {genre.name} · {genre.count}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <h3 className="text-sm font-semibold text-white">Recent Activity</h3>
            <div className="mt-4 space-y-3">
              {insights.recent_activity.length === 0 ? (
                <p className="text-sm text-white/50">No recent activity recorded yet.</p>
              ) : (
                insights.recent_activity.map((event) => (
                  <div key={event.id} className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 px-4 py-3">
                    <div>
                      <p className="text-sm font-medium capitalize text-white">{formatEventLabel(event.event_type)}</p>
                      <p className="mt-1 text-xs text-white/45">{formatRelativeTimestamp(event.created_at)}</p>
                    </div>
                    <span className="text-xs text-white/45">
                      {event.movie_id ? `Movie #${event.movie_id}` : "Account activity"}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
            <h2 className="text-xl font-semibold text-white">Favorite Movies</h2>
            <div className="mt-5 space-y-4">
              {profile.favorite_movies.length === 0 ? (
                <p className="text-sm text-white/55">No favorite movies yet.</p>
              ) : (
                profile.favorite_movies.map((movie) => (
                  <Link key={movie.id} href={`/movies/${movie.id}`} className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-white/20 hover:bg-white/[0.05]">
                    <div className="relative h-20 w-14 shrink-0 overflow-hidden rounded-xl">
                      <Image
                        src={movie.poster_url}
                        alt={`${movie.title} poster`}
                        fill
                        sizes="56px"
                        className="object-cover"
                      />
                    </div>
                    <div className="min-w-0">
                      <h3 className="truncate text-base font-semibold text-white">{movie.title}</h3>
                      <p className="mt-1 text-sm text-white/50">{movie.release_year} · {formatDuration(movie.duration_minutes)}</p>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
            <h2 className="text-xl font-semibold text-white">Watchlist</h2>
            <div className="mt-5 space-y-4">
              {profile.watchlist_movies.length === 0 ? (
                <p className="text-sm text-white/55">Your watchlist is empty.</p>
              ) : (
                profile.watchlist_movies.map((movie) => (
                  <Link key={movie.id} href={`/movies/${movie.id}`} className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-white/20 hover:bg-white/[0.05]">
                    <div className="relative h-20 w-14 shrink-0 overflow-hidden rounded-xl">
                      <Image
                        src={movie.poster_url}
                        alt={`${movie.title} poster`}
                        fill
                        sizes="56px"
                        className="object-cover"
                      />
                    </div>
                    <div className="min-w-0">
                      <h3 className="truncate text-base font-semibold text-white">{movie.title}</h3>
                      <p className="mt-1 text-sm text-white/50">{movie.release_year} · {movie.average_rating.toFixed(1)} avg</p>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-white">Recent Reviews</h2>
            <p className="mt-2 text-sm text-white/55">Your latest thoughts across the catalog.</p>
          </div>
          <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-white/65">
            {profile.review_count} total
          </span>
        </div>
        <div className="mt-5 space-y-4">
          {profile.recent_reviews.length === 0 ? (
            <p className="text-sm text-white/55">You have not written any reviews yet.</p>
          ) : (
            profile.recent_reviews.map((review) => (
              <article key={review.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-[#ff8b92]">{review.movie_title}</p>
                    <h3 className="mt-1 text-lg font-semibold text-white">{review.title}</h3>
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
      </section>
    </div>
  );
}
