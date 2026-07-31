import type { MovieCardProps } from "@/components/cards/MovieCard";
import Footer from "@/components/layout/Footer";
import Hero from "@/components/home/Hero";
import MovieRow from "@/components/home/MovieRow";
import Navbar from "@/components/layout/Navbar";

const poster = (seed: string) => `url(https://picsum.photos/seed/${seed}/400/600)`;

const movieRows: { title: string; movies: MovieCardProps[] }[] = [
  {
    title: "Trending Now",
    movies: [
      { title: "Neon Horizon", year: 2025, duration: "2h 08m", rating: 8.7, image: poster("neon-horizon") },
      { title: "The Last Signal", year: 2024, duration: "1h 54m", rating: 8.3, image: poster("last-signal") },
      { title: "After the Silence", year: 2025, duration: "2h 16m", rating: 9.1, image: poster("after-silence") },
      { title: "Parallel Lines", year: 2023, duration: "1h 47m", rating: 8.5, image: poster("parallel-lines") },
      { title: "Midnight Runway", year: 2024, duration: "2h 02m", rating: 8.8, image: poster("midnight-runway") },
      { title: "Echoes of Earth", year: 2025, duration: "1h 39m", rating: 8.9, image: poster("echoes-earth") },
    ],
  },
  {
    title: "Continue Watching",
    movies: [
      { title: "The Quiet City", year: 2024, duration: "1h 51m", rating: 8.1, image: poster("quiet-city") },
      { title: "Gravity Falls", year: 2023, duration: "2h 10m", rating: 8.6, image: poster("gravity-falls") },
      { title: "The Long Way Home", year: 2025, duration: "1h 45m", rating: 8.4, image: poster("long-way-home") },
      { title: "Static Hearts", year: 2024, duration: "2h 04m", rating: 7.9, image: poster("static-hearts") },
      { title: "Blue Hour", year: 2023, duration: "1h 38m", rating: 8.2, image: poster("blue-hour") },
      { title: "Northbound", year: 2025, duration: "2h 21m", rating: 8.8, image: poster("northbound") },
    ],
  },
  {
    title: "Action Movies",
    movies: [
      { title: "Velocity", year: 2025, duration: "2h 12m", rating: 8.5, image: poster("velocity") },
      { title: "Iron Divide", year: 2024, duration: "1h 58m", rating: 8.0, image: poster("iron-divide") },
      { title: "Redline Protocol", year: 2023, duration: "2h 06m", rating: 8.3, image: poster("redline-protocol") },
      { title: "Final Pursuit", year: 2025, duration: "1h 49m", rating: 8.7, image: poster("final-pursuit") },
      { title: "Blackout City", year: 2024, duration: "2h 18m", rating: 8.1, image: poster("blackout-city") },
      { title: "Wild Frontier", year: 2023, duration: "1h 56m", rating: 7.8, image: poster("wild-frontier") },
    ],
  },
  {
    title: "Comedy",
    movies: [
      { title: "Good Company", year: 2025, duration: "1h 42m", rating: 8.4, image: poster("good-company") },
      { title: "Roommates", year: 2024, duration: "1h 36m", rating: 7.9, image: poster("roommates") },
      { title: "Second Opinion", year: 2023, duration: "1h 48m", rating: 8.2, image: poster("second-opinion") },
      { title: "Weekend Plans", year: 2025, duration: "1h 40m", rating: 8.0, image: poster("weekend-plans") },
      { title: "The Big Detour", year: 2024, duration: "1h 52m", rating: 8.3, image: poster("big-detour") },
      { title: "Perfectly Normal", year: 2023, duration: "1h 34m", rating: 7.7, image: poster("perfectly-normal") },
    ],
  },
  {
    title: "Top Rated",
    movies: [
      { title: "A Different Sky", year: 2022, duration: "2h 20m", rating: 9.4, image: poster("different-sky") },
      { title: "The Memory Keeper", year: 2021, duration: "2h 08m", rating: 9.2, image: poster("memory-keeper") },
      { title: "Orbit", year: 2020, duration: "2h 16m", rating: 9.1, image: poster("orbit") },
      { title: "The Crossing", year: 2022, duration: "1h 57m", rating: 9.0, image: poster("the-crossing") },
      { title: "Paper Kingdom", year: 2021, duration: "2h 04m", rating: 8.9, image: poster("paper-kingdom") },
      { title: "Far From Here", year: 2020, duration: "1h 51m", rating: 8.8, image: poster("far-from-here") },
    ],
  },
  {
    title: "Recently Added",
    movies: [
      { title: "The Open Sea", year: 2026, duration: "2h 01m", rating: 8.8, image: poster("open-sea") },
      { title: "Everywhere at Once", year: 2026, duration: "1h 59m", rating: 8.6, image: poster("everywhere-once") },
      { title: "Glass House", year: 2026, duration: "1h 44m", rating: 8.1, image: poster("glass-house") },
      { title: "Signal Fire", year: 2026, duration: "2h 14m", rating: 8.9, image: poster("signal-fire") },
      { title: "Golden State", year: 2026, duration: "1h 53m", rating: 8.0, image: poster("golden-state") },
      { title: "The Witness", year: 2026, duration: "1h 46m", rating: 8.5, image: poster("the-witness") },
    ],
  },
  {
    title: "Watch Continue",
    movies: [
      { title: "The Quiet City", year: 2024, duration: "1h 51m", rating: 8.1, image: poster("quiet-city-continue") },
      { title: "Gravity Falls", year: 2023, duration: "2h 10m", rating: 8.6, image: poster("gravity-falls-continue") },
      { title: "The Long Way Home", year: 2025, duration: "1h 45m", rating: 8.4, image: poster("long-way-home-continue") },
      { title: "Static Hearts", year: 2024, duration: "2h 04m", rating: 7.9, image: poster("static-hearts-continue") },
      { title: "Blue Hour", year: 2023, duration: "1h 38m", rating: 8.2, image: poster("blue-hour-continue") },
      { title: "Northbound", year: 2025, duration: "2h 21m", rating: 8.8, image: poster("northbound-continue") },
    ],
  },
];

const rowOrder = [
  "Trending Now",
  "Continue Watching",
  "Watch Continue",
  "Recently Added",
  "Top Rated",
  "Action Movies",
  "Comedy",
];

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <main>
        <Hero />
        <section id="movies" className="space-y-14 bg-black px-6 py-20 sm:px-8 lg:space-y-16 lg:px-10 lg:py-28">
          <div className="mx-auto w-full max-w-7xl">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-[#E50914]">
              Curated for you
            </p>
            <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Find your next favorite
            </h2>
          </div>
          <div className="mx-auto flex w-full max-w-7xl flex-col gap-14 lg:gap-16">
            {rowOrder.map((title) => {
              const row = movieRows.find((movieRow) => movieRow.title === title);

              return row ? <MovieRow key={row.title} {...row} /> : null;
            })}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
