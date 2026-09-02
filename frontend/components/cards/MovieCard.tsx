import Link from "next/link";

export interface MovieCardProps {
  id: number;
  title: string;
  year: number;
  duration: string;
  rating: number;
  image: string;
}

export function MovieCardSkeleton() {
  return (
    <div aria-label="Loading movie" className="animate-pulse overflow-hidden rounded-xl border border-white/10 bg-[#111111]">
      <div className="aspect-[2/3] bg-white/10" />
      <div className="space-y-3 p-4">
        <div className="h-4 w-3/4 rounded bg-white/10" />
        <div className="h-3 w-1/2 rounded bg-white/10" />
      </div>
    </div>
  );
}

export default function MovieCard({
  id,
  title,
  year,
  duration,
  rating,
  image,
}: MovieCardProps) {
  return (
    <Link href={`/movies/${id}`} aria-label={`Open ${title} preview`} className="group block min-w-0 rounded-xl focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#E50914]">
      <article className="overflow-hidden rounded-xl border border-white/10 bg-[#111111] shadow-lg shadow-black/20 transition-all duration-300 ease-out group-hover:z-10 group-hover:scale-[1.03] group-hover:border-white/20 group-hover:shadow-[0_16px_40px_rgba(229,9,20,0.28)] group-focus-visible:scale-[1.03] group-focus-visible:border-white/20 group-focus-visible:shadow-[0_16px_40px_rgba(229,9,20,0.28)]">
      <div
        aria-label={`${title} poster placeholder`}
        className="relative aspect-[2/3] overflow-hidden bg-cover bg-center"
        role="img"
        style={{ backgroundImage: image }}
      >
        <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-transparent to-transparent" />
        <span className="absolute right-3 top-3 rounded-md bg-black/70 px-2 py-1 text-xs font-semibold text-white backdrop-blur-sm">
          ★ {rating.toFixed(1)}
        </span>
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black/25 opacity-0 transition-opacity duration-300 group-hover:opacity-100 group-focus-within:opacity-100">
          <span
            aria-hidden="true"
            className="flex h-11 w-11 items-center justify-center rounded-full bg-[#E50914] text-white shadow-lg shadow-black/40 transition-transform hover:scale-110 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
          >
            <svg aria-hidden="true" className="ml-0.5 h-5 w-5 fill-current" viewBox="0 0 24 24">
              <path d="M8 5.14v13.72a1 1 0 0 0 1.54.84l10.14-6.86a1 1 0 0 0 0-1.68L9.54 4.3A1 1 0 0 0 8 5.14Z" />
            </svg>
          </span>
          <span className="rounded-md bg-black/70 px-2 py-1 text-xs font-medium text-white backdrop-blur-md">
            {year} · ★ {rating.toFixed(1)}
          </span>
        </div>
      </div>
      <div className="p-4">
        <h2 className="truncate text-base font-semibold text-white">{title}</h2>
        <div className="mt-2 flex items-center gap-2 text-xs text-white/50">
          <span>{year}</span>
          <span aria-hidden="true" className="h-1 w-1 rounded-full bg-white/30" />
          <span>{duration}</span>
        </div>
      </div>
      </article>
    </Link>
  );
}
