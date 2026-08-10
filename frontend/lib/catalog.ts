import { resolveApiBaseUrl } from "@/lib/auth";

export interface Genre {
  id: number;
  name: string;
}

export interface Movie {
  id: number;
  title: string;
  description: string;
  release_year: number;
  duration_minutes: number;
  poster_url: string;
  trailer_url: string;
  maturity_rating: string;
  language: string;
  genres: Genre[];
  average_rating: number;
  total_ratings: number;
  review_count: number;
  created_at: string;
  updated_at: string;
}

export interface MovieListResponse {
  items: Movie[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface RecommendationResponse {
  recommended_movies: Movie[];
  recommended_genres: Genre[];
  reason_for_recommendation: string;
}

export interface AISearchResponse {
  matching_movies: Movie[];
  reasoning: string;
  confidence: number;
}

export interface MovieSummary {
  movie_id: number;
  short_summary: string;
  long_summary: string;
  main_themes: string[];
  viewer_type: string;
  provider_name: string;
  generated_at: string;
  updated_at: string;
}

export interface ContinueWatchingItem {
  id: number;
  progress_percentage: number;
  last_watched: string;
  completed: boolean;
  movie: Movie;
}

export interface HomeResponse {
  continue_watching: ContinueWatchingItem[];
  recommended: Movie[];
  trending: Movie[];
  favorites: Movie[];
  recently_added: Movie[];
  top_rated: Movie[];
  popular_genres: Genre[];
}

function createUrl(path: string, params?: Record<string, string | number | undefined>) {
  const url = new URL(path, resolveApiBaseUrl());

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  return url.toString();
}

async function fetchJson<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
  const response = await fetch(createUrl(path, params), {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchMovies(params?: Record<string, string | number | undefined>) {
  return fetchJson<MovieListResponse>("/movies", params);
}

export async function fetchMovie(id: number) {
  return fetchJson<Movie>(`/movies/${id}`);
}

export async function fetchGenres() {
  return fetchJson<Genre[]>("/genres");
}

export async function fetchTrendingMovies() {
  return fetchJson<Movie[]>("/movies/trending");
}

export async function searchMoviesWithAI(query: string) {
  const response = await fetch(createUrl("/search/ai"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as AISearchResponse;
}

export async function fetchMovieSummary(id: number) {
  return fetchJson<MovieSummary>(`/movies/${id}/summary`);
}

export interface Review {
  id: number;
  movie_id: number;
  user_id: string;
  username: string;
  title: string;
  body: string;
  rating: number;
  created_at: string;
  updated_at: string;
}

export interface WatchlistItem {
  id: number;
  created_at: string;
  movie: Movie;
}

export interface FavoriteItem {
  id: number;
  created_at: string;
  movie: Movie;
}

export interface ProfileReview extends Review {
  movie_title: string;
}

export interface Profile {
  username: string;
  email: string;
  account_creation_date: string;
  favorite_count: number;
  watchlist_count: number;
  review_count: number;
  average_rating_given: number;
  recent_reviews: ProfileReview[];
  favorite_movies: Movie[];
  watchlist_movies: Movie[];
}

export function formatDuration(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes.toString().padStart(2, "0")}m`;
}
