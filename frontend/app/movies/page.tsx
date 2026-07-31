import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";
import MovieFilters from "@/components/movies/MovieFilters";
import MovieGridCard from "@/components/movies/MovieGridCard";
import PaginationControls from "@/components/movies/PaginationControls";
import { fetchGenres, fetchMovies } from "@/lib/catalog";

type SearchParams = Promise<{
  search?: string;
  genre?: string;
  language?: string;
  sort_by?: string;
  sort_order?: string;
  page?: string;
}>;

function createPageHref(page: number, params: URLSearchParams) {
  const nextParams = new URLSearchParams(params);
  nextParams.set("page", String(page));
  const query = nextParams.toString();
  return query ? `/movies?${query}` : "/movies";
}

export default async function MoviesPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const page = Math.max(1, Number(params.page ?? "1") || 1);
  const search = params.search ?? "";
  const genre = params.genre ?? "";
  const language = params.language ?? "";
  const sortBy = params.sort_by === "release_year" ? "release_year" : "title";
  const sortOrder = params.sort_order === "desc" ? "desc" : "asc";
  const queryParams = new URLSearchParams();

  if (search) queryParams.set("search", search);
  if (genre) queryParams.set("genre", genre);
  if (language) queryParams.set("language", language);
  queryParams.set("sort_by", sortBy);
  queryParams.set("sort_order", sortOrder);

  const [genres, movieList] = await Promise.all([
    fetchGenres(),
    fetchMovies({
      search,
      genre,
      language,
      sort_by: sortBy,
      sort_order: sortOrder,
      page,
      page_size: 8,
    }),
  ]);

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 pb-16 pt-28 sm:px-8 lg:px-10 lg:pb-24 lg:pt-32">
        <section className="space-y-5">
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-[#E50914]">Movie Catalog</p>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl space-y-3">
              <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Browse every story in StreamSphere
              </h1>
              <p className="text-base leading-7 text-white/65">
                Search by title, filter by genre or language, and move through the catalog with server-side pagination.
              </p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/[0.03] px-5 py-4 text-sm text-white/65">
              <span className="block text-xs font-semibold uppercase tracking-[0.22em] text-white/40">Available now</span>
              <span className="mt-1 block text-3xl font-semibold tracking-tight text-white">{movieList.total}</span>
            </div>
          </div>
        </section>

        <MovieFilters
          genres={genres}
          search={search}
          genre={genre}
          language={language}
          sortBy={sortBy}
          sortOrder={sortOrder}
        />

        <section className="space-y-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight text-white">Results</h2>
              <p className="text-sm text-white/55">
                Showing {movieList.items.length} of {movieList.total} titles
              </p>
            </div>
          </div>

          {movieList.items.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-white/12 bg-[#0d0d0d] px-6 py-14 text-center">
              <h3 className="text-xl font-semibold text-white">No movies matched these filters</h3>
              <p className="mt-3 text-sm leading-6 text-white/60">
                Try clearing a filter or broadening the search term.
              </p>
            </div>
          ) : (
            <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
              {movieList.items.map((movie) => (
                <MovieGridCard key={movie.id} movie={movie} />
              ))}
            </div>
          )}
        </section>

        <PaginationControls
          page={movieList.page}
          totalPages={movieList.total_pages}
          createPageHref={(nextPage) => createPageHref(nextPage, queryParams)}
        />
      </main>
      <Footer />
    </div>
  );
}
