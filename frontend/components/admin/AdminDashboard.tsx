"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { clearAccessToken, fetchWithAuth, getAccessToken } from "@/lib/auth";
import type {
  AdminReview,
  AdminStats,
  AdminUser,
  Movie,
  PlatformAnalytics,
  Profile,
} from "@/lib/catalog";
import { formatRelativeTimestamp } from "@/lib/catalog";

type DashboardState = {
  profile: Profile;
  stats: AdminStats;
  users: AdminUser[];
  movies: Movie[];
  reviews: AdminReview[];
  analytics: PlatformAnalytics;
};

export default function AdminDashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<DashboardState | null>(null);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      if (!getAccessToken()) {
        router.replace("/login");
        return;
      }

      try {
        const profile = await fetchWithAuth<Profile>("/profile");
        if (!profile.is_admin) {
          router.replace("/profile");
          return;
        }

        const [stats, users, movies, reviews, analytics] = await Promise.all([
          fetchWithAuth<AdminStats>("/admin/stats"),
          fetchWithAuth<AdminUser[]>("/admin/users"),
          fetchWithAuth<Movie[]>("/admin/movies"),
          fetchWithAuth<AdminReview[]>("/admin/reviews"),
          fetchWithAuth<PlatformAnalytics>("/admin/analytics"),
        ]);

        if (!active) {
          return;
        }

        setState({ profile, stats, users, movies, reviews, analytics });
        setError(null);
      } catch (requestError) {
        if (!active) {
          return;
        }

        const message = requestError instanceof Error ? requestError.message : "Unable to load the admin dashboard.";
        if (message.includes("Could not validate credentials")) {
          clearAccessToken();
          router.replace("/login");
          return;
        }

        if (message.includes("Administrator access required")) {
          router.replace("/profile");
          return;
        }

        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      active = false;
    };
  }, [router]);

  async function toggleUserStatus(user: AdminUser) {
    const updated = await fetchWithAuth<AdminUser>(`/admin/users/${user.id}/status`, {
      method: "PUT",
      body: JSON.stringify({ is_active: !user.is_active }),
    });
    setState((current) =>
      current
        ? {
            ...current,
            users: current.users.map((entry) => (entry.id === updated.id ? updated : entry)),
          }
        : current,
    );
  }

  async function deleteReview(reviewId: number) {
    await fetchWithAuth<{ detail: string }>(`/admin/reviews/${reviewId}`, {
      method: "DELETE",
    });
    setState((current) =>
      current
        ? {
            ...current,
            reviews: current.reviews.filter((review) => review.id !== reviewId),
            stats: {
              ...current.stats,
              total_reviews: Math.max(0, current.stats.total_reviews - 1),
            },
          }
        : current,
    );
  }

  if (loading) {
    return <p className="text-sm text-white/60">Loading admin dashboard...</p>;
  }

  if (error || !state) {
    return (
      <div className="rounded-[2rem] border border-dashed border-white/12 bg-[#0d0d0d] p-8 text-center">
        <h2 className="text-2xl font-semibold text-white">Admin dashboard unavailable</h2>
        <p className="mt-3 text-sm leading-6 text-white/60">{error ?? "Unable to load admin data."}</p>
        <Link href="/profile" className="mt-6 inline-flex h-12 items-center justify-center rounded-2xl bg-[#E50914] px-6 text-sm font-semibold text-white transition hover:bg-[#c50b14]">
          Return to profile
        </Link>
      </div>
    );
  }

  const { stats, users, movies, reviews, analytics } = state;

  return (
    <div className="space-y-8">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ["Users", stats.total_users],
          ["Movies", stats.total_movies],
          ["Reviews", stats.total_reviews],
          ["Ratings", stats.total_ratings],
          ["Favorites", stats.total_favorites],
          ["Watchlist Entries", stats.total_watchlist_entries],
          ["AI Searches", stats.total_ai_searches],
          ["Recommendations", stats.total_recommendations_generated],
        ].map(([label, value]) => (
          <div key={label} className="rounded-[1.75rem] border border-white/10 bg-[#101010] p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/40">{label}</p>
            <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
          <h2 className="text-xl font-semibold text-white">Recent Users</h2>
          <div className="mt-5 space-y-3">
            {users.map((user) => (
              <div key={user.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-white">{user.username}</p>
                    <p className="mt-1 text-sm text-white/55">{user.email}</p>
                    <p className="mt-2 text-xs text-white/40">{formatRelativeTimestamp(user.created_at)}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => void toggleUserStatus(user)}
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      user.is_active ? "bg-emerald-500/15 text-emerald-300" : "bg-white/10 text-white/60"
                    }`}
                  >
                    {user.is_active ? "Active" : "Inactive"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
          <h2 className="text-xl font-semibold text-white">Recent Movies</h2>
          <div className="mt-5 space-y-3">
            {movies.map((movie) => (
              <Link key={movie.id} href={`/movies/${movie.id}`} className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-white/20 hover:bg-white/[0.05]">
                <img src={movie.poster_url} alt={`${movie.title} poster`} className="h-16 w-12 rounded-lg object-cover" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-white">{movie.title}</p>
                  <p className="mt-1 text-xs text-white/50">{movie.release_year} · {movie.language}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
          <h2 className="text-xl font-semibold text-white">Popular Genres</h2>
          <div className="mt-5 space-y-3">
            {analytics.popular_genres.length === 0 ? (
              <p className="text-sm text-white/55">No analytics yet.</p>
            ) : (
              analytics.popular_genres.map((genre) => (
                <div key={genre.name} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3">
                  <span className="text-sm text-white">{genre.name}</span>
                  <span className="text-xs text-white/55">{genre.count}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-white">Review Moderation</h2>
              <p className="mt-2 text-sm text-white/55">Recent reviews with one-click removal for moderation.</p>
            </div>
          </div>
          <div className="mt-5 space-y-4">
            {reviews.map((review) => (
              <article key={review.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm text-[#ff8b92]">{review.movie_title}</p>
                    <h3 className="mt-1 text-lg font-semibold text-white">{review.title}</h3>
                    <p className="mt-2 text-xs text-white/45">by {review.username}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => void deleteReview(review.id)}
                    className="rounded-full border border-white/10 px-3 py-1 text-xs font-semibold text-white/70 transition hover:border-[#E50914]/40 hover:text-white"
                  >
                    Remove
                  </button>
                </div>
                <p className="mt-4 text-sm leading-7 text-white/65">{review.body}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-[#0d0d0d] p-6">
          <h2 className="text-xl font-semibold text-white">Platform Activity</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-white/40">Most Viewed</p>
              <div className="mt-4 space-y-2">
                {analytics.most_viewed_movies.slice(0, 5).map((entry) => (
                  <div key={entry.movie.id} className="flex items-center justify-between text-sm text-white/75">
                    <span className="truncate pr-4">{entry.movie.title}</span>
                    <span>{entry.count}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-white/40">Top Rated</p>
              <div className="mt-4 space-y-2">
                {analytics.top_rated_movies.slice(0, 5).map((entry) => (
                  <div key={entry.movie.id} className="flex items-center justify-between text-sm text-white/75">
                    <span className="truncate pr-4">{entry.movie.title}</span>
                    <span>{entry.count.toFixed(1)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-white">Daily Active Users</p>
              <span className="text-xs text-white/45">{analytics.ai_search_volume} AI searches</span>
            </div>
            <div className="mt-4 space-y-2">
              {analytics.daily_active_users.map((entry) => (
                <div key={entry.day} className="flex items-center justify-between text-sm text-white/70">
                  <span>{entry.day}</span>
                  <span>{entry.active_users}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
