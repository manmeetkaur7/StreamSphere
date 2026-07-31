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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

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

export function formatDuration(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes.toString().padStart(2, "0")}m`;
}
