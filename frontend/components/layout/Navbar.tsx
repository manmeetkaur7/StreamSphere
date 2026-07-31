import Link from "next/link";

const navigationItems = [
  { label: "Home", href: "/" },
  { label: "Movies", href: "/movies" },
  { label: "TV Shows", href: "/#tv-shows" },
  { label: "My List", href: "/#my-list" },
];

function SearchIcon() {
  return (
    <svg
      aria-hidden="true"
      className="h-5 w-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="1.8"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-4.35-4.35m2.1-5.4a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Z" />
    </svg>
  );
}

function BellIcon() {
  return (
    <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.86 18a3 3 0 0 1-5.72 0M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9Z" />
    </svg>
  );
}

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 -mb-20 border-b border-white/5 bg-black/20 backdrop-blur-md">
      <nav
        aria-label="Main navigation"
        className="mx-auto flex h-20 w-full max-w-7xl items-center justify-between px-6 sm:px-8 lg:px-10"
      >
        <Link
          href="/"
          className="text-xl font-semibold tracking-tight text-white transition-opacity hover:opacity-80 sm:text-2xl"
        >
          Stream<span className="text-[#E50914]">Sphere</span>
        </Link>

        <div className="hidden items-center gap-7 md:flex lg:gap-9">
          {navigationItems.map((item, index) => (
            <Link
              key={item.label}
              href={item.href}
              className={`text-sm transition-colors hover:text-white ${
                index === 0 ? "font-medium text-white" : "text-white/65"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-3 text-white sm:gap-5">
          <button
            type="button"
            aria-label="Search"
            className="rounded-full p-2 transition-colors hover:bg-white/10 hover:text-[#E50914] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
          >
            <SearchIcon />
          </button>
          <button
            type="button"
            aria-label="View notifications"
            className="relative rounded-full p-2 transition-colors hover:bg-white/10 hover:text-[#E50914] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
          >
            <BellIcon />
            <span aria-hidden="true" className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-[#E50914]" />
          </button>
          <button
            type="button"
            aria-label="Open user profile"
            className="flex h-9 w-9 items-center justify-center rounded-full border border-white/20 bg-gradient-to-br from-[#E50914] to-[#7f0710] text-xs font-semibold text-white transition-transform hover:scale-105 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
          >
            SS
          </button>
          <Link
            href="/login"
            className="hidden rounded-md border border-white/20 px-4 py-2 text-sm font-medium text-white transition-all hover:border-white/50 hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914] sm:inline-flex"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="hidden rounded-md bg-[#E50914] px-4 py-2 text-sm font-semibold text-white transition-all hover:-translate-y-0.5 hover:bg-[#b80710] hover:shadow-[0_8px_20px_rgba(229,9,20,0.3)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914] lg:inline-flex"
          >
            Sign Up
          </Link>
        </div>
      </nav>
    </header>
  );
}
