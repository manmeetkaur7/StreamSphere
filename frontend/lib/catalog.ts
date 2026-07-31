import { API_BASE_URL } from "@/lib/auth";

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

function createUrl(path: string, params?: Record<string, string | number | undefined>) {
  const url = new URL(path, API_BASE_URL);

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
