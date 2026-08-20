"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { clearAccessToken, fetchWithAuth, getAccessToken } from "@/lib/auth";
import type { Profile } from "@/lib/catalog";
import { formatDuration } from "@/lib/catalog";

export default function ProfileDashboard() {
  const [authenticated, setAuthenticated] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(null);
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
        const payload = await fetchWithAuth<Profile>("/profile");
        if (!active) {
          return;
        }
        setProfile(payload);
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

  if (!authenticated || !profile) {
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
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Account</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white">{profile.username}</h1>
          <p className="mt-2 text-sm text-white/55">{profile.email}</p>
          <p className="mt-4 text-sm text-white/45">
            Member since {new Date(profile.account_creation_date).toLocaleDateString()}
          </p>
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

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
          <h2 className="text-xl font-semibold text-white">Favorite Movies</h2>
          <div className="mt-5 space-y-4">
            {profile.favorite_movies.length === 0 ? (
              <p className="text-sm text-white/55">No favorite movies yet.</p>
            ) : (
              profile.favorite_movies.map((movie) => (
                <Link key={movie.id} href={`/movies/${movie.id}`} className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-white/20 hover:bg-white/[0.05]">
                  <img src={movie.poster_url} alt={`${movie.title} poster`} className="h-20 w-14 rounded-xl object-cover" />
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
                  <img src={movie.poster_url} alt={`${movie.title} poster`} className="h-20 w-14 rounded-xl object-cover" />
                  <div className="min-w-0">
                    <h3 className="truncate text-base font-semibold text-white">{movie.title}</h3>
                    <p className="mt-1 text-sm text-white/50">{movie.release_year} · {movie.average_rating.toFixed(1)} avg</p>
                  </div>
                </Link>
              ))
            )}
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
