"use client";

import { useRef } from "react";
import MovieCard, { MovieCardSkeleton, type MovieCardProps } from "@/components/cards/MovieCard";

interface MovieRowProps {
  title: string;
  movies: MovieCardProps[];
  isLoading?: boolean;
}

function ArrowIcon({ direction }: { direction: "left" | "right" }) {
  return (
    <svg
      aria-hidden="true"
      className="h-6 w-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="2"
    >
      {direction === "left" ? (
        <path strokeLinecap="round" strokeLinejoin="round" d="m15 19-7-7 7-7" />
      ) : (
        <path strokeLinecap="round" strokeLinejoin="round" d="m9 5 7 7-7 7" />
      )}
    </svg>
  );
}

export default function MovieRow({ title, movies, isLoading = false }: MovieRowProps) {
  const rowRef = useRef<HTMLDivElement>(null);
  const rowId = `${title.toLowerCase().replaceAll(" ", "-")}-content`;

  const scrollRow = (direction: "left" | "right") => {
    rowRef.current?.scrollBy({
      behavior: "smooth",
      left: direction === "left" ? -640 : 640,
    });
  };

  return (
    <section className="group/row relative" aria-labelledby={`${title.toLowerCase().replaceAll(" ", "-")}-heading`}>
      <h2
        id={`${title.toLowerCase().replaceAll(" ", "-")}-heading`}
        className="mb-5 text-xl font-semibold tracking-tight text-white sm:text-2xl"
      >
        {title}
      </h2>
      <div className="relative">
        <button
          type="button"
          aria-label={`Scroll ${title} left`}
          aria-controls={rowId}
          onClick={() => scrollRow("left")}
          className="absolute left-2 top-1/2 z-20 flex h-12 w-10 -translate-y-1/2 items-center justify-center rounded-md border border-white/10 bg-black/75 text-white opacity-100 shadow-xl backdrop-blur-sm transition-all hover:bg-[#E50914] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914] md:opacity-0 md:group-hover/row:opacity-100"
        >
          <ArrowIcon direction="left" />
        </button>
        <button
          type="button"
          aria-label={`Scroll ${title} right`}
          aria-controls={rowId}
          onClick={() => scrollRow("right")}
          className="absolute right-2 top-1/2 z-20 flex h-12 w-10 -translate-y-1/2 items-center justify-center rounded-md border border-white/10 bg-black/75 text-white opacity-100 shadow-xl backdrop-blur-sm transition-all hover:bg-[#E50914] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914] md:opacity-0 md:group-hover/row:opacity-100"
        >
          <ArrowIcon direction="right" />
        </button>
        <div
          id={rowId}
          ref={rowRef}
          aria-label={`${title} movie list`}
          role="region"
          tabIndex={0}
          className="flex snap-x snap-mandatory gap-4 overflow-x-auto scroll-smooth pb-4 outline-none [scrollbar-width:none] [&::-webkit-scrollbar]:hidden focus-visible:ring-2 focus-visible:ring-[#E50914] sm:gap-5"
        >
          {isLoading
            ? Array.from({ length: 6 }, (_, index) => (
                <div key={`movie-skeleton-${index}`} className="w-[150px] flex-none snap-start sm:w-[190px] lg:w-[220px]">
                  <MovieCardSkeleton />
                </div>
              ))
            : movies.map((movie) => (
                <div key={movie.title} className="w-[150px] flex-none snap-start sm:w-[190px] lg:w-[220px]">
                  <MovieCard {...movie} />
                </div>
              ))}
        </div>
      </div>
    </section>
  );
}
