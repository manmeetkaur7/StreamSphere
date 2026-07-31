import Link from "next/link";

import type { Genre } from "@/lib/catalog";

interface MovieFiltersProps {
  genres: Genre[];
  search: string;
  genre: string;
  language: string;
  sortBy: string;
  sortOrder: string;
}

export default function MovieFilters({
  genres,
  search,
  genre,
  language,
  sortBy,
  sortOrder,
}: MovieFiltersProps) {
  return (
    <form className="grid gap-4 rounded-3xl border border-white/10 bg-[#0d0d0d] p-5 shadow-[0_24px_60px_rgba(0,0,0,0.24)] lg:grid-cols-[minmax(0,2fr)_repeat(4,minmax(0,1fr))]">
      <label className="space-y-2">
        <span className="text-xs font-semibold uppercase tracking-[0.22em] text-white/45">Search</span>
        <input
          type="search"
          name="search"
          defaultValue={search}
          placeholder="Search by title"
          className="h-12 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30"
        />
      </label>

      <label className="space-y-2">
        <span className="text-xs font-semibold uppercase tracking-[0.22em] text-white/45">Genre</span>
        <select
          name="genre"
          defaultValue={genre}
          className="h-12 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30"
        >
          <option value="">All genres</option>
          {genres.map((genreOption) => (
            <option key={genreOption.id} value={genreOption.name}>
              {genreOption.name}
            </option>
          ))}
        </select>
      </label>

      <label className="space-y-2">
        <span className="text-xs font-semibold uppercase tracking-[0.22em] text-white/45">Language</span>
        <input
          type="text"
          name="language"
          defaultValue={language}
          placeholder="English"
          className="h-12 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30"
        />
      </label>

      <label className="space-y-2">
        <span className="text-xs font-semibold uppercase tracking-[0.22em] text-white/45">Sort by</span>
        <select
          name="sort_by"
          defaultValue={sortBy}
          className="h-12 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30"
        >
          <option value="title">Title</option>
          <option value="release_year">Release year</option>
        </select>
      </label>

      <label className="space-y-2">
        <span className="text-xs font-semibold uppercase tracking-[0.22em] text-white/45">Order</span>
        <select
          name="sort_order"
          defaultValue={sortOrder}
          className="h-12 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 text-sm text-white outline-none transition focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/30"
        >
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </label>

      <div className="flex items-end gap-3 lg:col-span-full">
        <button
          type="submit"
          className="inline-flex h-12 items-center justify-center rounded-2xl bg-[#E50914] px-6 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-[#c50b14] hover:shadow-[0_12px_24px_rgba(229,9,20,0.3)]"
        >
          Apply Filters
        </button>
        <Link
          href="/movies"
          className="inline-flex h-12 items-center justify-center rounded-2xl border border-white/15 px-6 text-sm font-semibold text-white/70 transition hover:border-white/35 hover:bg-white/[0.04] hover:text-white"
        >
          Reset
        </Link>
      </div>
    </form>
  );
}
