export default function Hero() {
  return (
    <section
      id="home"
      className="relative flex h-screen min-h-[680px] items-end overflow-hidden bg-black"
    >
      <div
        aria-hidden="true"
        className="absolute inset-0 animate-[heroScale_20s_ease-in-out_infinite_alternate] bg-cover bg-center"
        style={{ backgroundImage: "url(https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=2400&q=85)" }}
      />
      <div
        aria-hidden="true"
        className="absolute inset-0 animate-[heroFade_1.2s_ease-out_both] bg-[linear-gradient(90deg,rgba(0,0,0,0.96)_0%,rgba(0,0,0,0.72)_42%,rgba(0,0,0,0.2)_100%)]"
      />
      <div aria-hidden="true" className="absolute inset-0 bg-[linear-gradient(0deg,#000_0%,rgba(0,0,0,0.58)_24%,transparent_68%)]" />

      <div className="relative z-10 mx-auto w-full max-w-7xl animate-[heroFade_1.2s_0.15s_ease-out_both] px-6 pb-16 pt-32 sm:px-8 sm:pb-24 lg:px-10 lg:pb-28">
        <div className="max-w-2xl">
          <p className="mb-5 text-sm font-semibold uppercase tracking-[0.3em] text-[#E50914]">
            Featured Movie
          </p>
          <h1 className="text-5xl font-semibold leading-[1.05] tracking-tight text-white sm:text-7xl lg:text-8xl">
            Interstellar
          </h1>
          <p className="mt-5 text-sm font-medium text-white/75 sm:text-base">
            Sci-Fi <span className="px-2 text-white/35">•</span> Adventure <span className="px-2 text-white/35">•</span> Drama
          </p>
          <p className="mt-4 text-sm font-semibold tracking-wide text-white sm:text-base">
            <span className="mr-2 text-[#E50914]">★★★★★</span> 9.4
          </p>
          <p className="mt-5 max-w-xl text-base leading-7 text-white/70 sm:text-lg sm:leading-8">
            A team of explorers travel beyond our galaxy in search of humanity&apos;s future.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <a
              href="#movies"
              className="inline-flex h-12 items-center justify-center rounded-md bg-[#E50914] px-7 text-sm font-semibold text-white transition-all hover:-translate-y-0.5 hover:bg-[#b80710] hover:shadow-[0_12px_28px_rgba(229,9,20,0.35)] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#E50914]"
            >
              ▶&nbsp; Play
            </a>
            <a
              href="#about"
              className="inline-flex h-12 items-center justify-center rounded-md border border-white/25 bg-white/10 px-7 text-sm font-semibold text-white transition-all hover:-translate-y-0.5 hover:border-white/50 hover:bg-white/20 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-white"
            >
              ⓘ&nbsp; More Info
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
