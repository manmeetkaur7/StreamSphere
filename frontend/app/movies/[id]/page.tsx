import Link from "next/link";
import { notFound } from "next/navigation";

import MovieEngagementClient from "@/components/movies/MovieEngagementClient";
import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";
import { fetchMovie } from "@/lib/catalog";

export default async function MovieDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const movieId = Number(id);

  if (!Number.isInteger(movieId) || movieId <= 0) {
    notFound();
  }

  let movie;
  try {
    movie = await fetchMovie(movieId);
  } catch {
    notFound();
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 pb-16 pt-28 sm:px-8 lg:px-10 lg:pb-24 lg:pt-32">
        <Link
          href="/movies"
          className="inline-flex w-fit items-center gap-2 text-sm font-semibold text-white/65 transition hover:text-white"
        >
          <span aria-hidden="true">←</span>
          Back to catalog
        </Link>

        <MovieEngagementClient initialMovie={movie} />
      </main>
      <Footer />
    </div>
  );
}
