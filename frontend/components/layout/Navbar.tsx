"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import NotificationCenter from "@/components/layout/NotificationCenter";
import { AUTH_STATE_CHANGE_EVENT, clearAccessToken, fetchWithAuth, getAccessToken } from "@/lib/auth";
import type { Profile } from "@/lib/catalog";

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

export default function Navbar() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [authenticated, setAuthenticated] = useState(() => Boolean(getAccessToken()));
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    let active = true;

    async function syncAuthenticationState() {
      const token = getAccessToken();
      if (!token) {
        if (active) {
          setAuthenticated(false);
          setProfile(null);
          setProfileMenuOpen(false);
        }
        return;
      }

      if (active) {
        setAuthenticated(true);
      }

      try {
        const payload = await fetchWithAuth<Profile>("/profile");
        if (!active || token !== getAccessToken()) {
          return;
        }
        setProfile(payload);
      } catch (error) {
        if (!active || token !== getAccessToken()) {
          return;
        }
        if (error instanceof Error && error.message.includes("Could not validate credentials")) {
          clearAccessToken();
        }
      }
    }

    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === "streamsphere_access_token") {
        void syncAuthenticationState();
      }
    };
    const handleAuthStateChange = () => void syncAuthenticationState();

    void syncAuthenticationState();
    window.addEventListener(AUTH_STATE_CHANGE_EVENT, handleAuthStateChange);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      active = false;
      window.removeEventListener(AUTH_STATE_CHANGE_EVENT, handleAuthStateChange);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  function handleSignOut() {
    clearAccessToken();
    setProfile(null);
    setAuthenticated(false);
    setProfileMenuOpen(false);
    router.replace("/");
    router.refresh();
  }

  const navigationItems = [
    { label: "Home", href: "/" },
    { label: "Movies", href: "/movies" },
    { label: "My List", href: "/profile" },
    { label: "Profile", href: "/profile" },
    ...(profile?.is_admin ? [{ label: "Admin", href: "/admin" }] : []),
  ];

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
          <Link
            href="/movies"
            aria-label="Search the movie catalog"
            className="rounded-full p-2 transition-colors hover:bg-white/10 hover:text-[#E50914] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
          >
            <SearchIcon />
          </Link>
          {authenticated ? <NotificationCenter authenticated={authenticated} /> : null}
          {authenticated ? (
            <div className="relative">
              <button
                type="button"
                aria-label="Open user menu"
                aria-controls="profile-menu"
                aria-expanded={profileMenuOpen}
                onClick={() => setProfileMenuOpen((open) => !open)}
                className="flex h-9 w-9 items-center justify-center rounded-full border border-white/20 bg-gradient-to-br from-[#E50914] to-[#7f0710] text-xs font-semibold uppercase text-white transition-transform hover:scale-105 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
              >
                {(profile?.username ?? "SS").slice(0, 2)}
              </button>
              {profileMenuOpen ? (
                <div id="profile-menu" className="absolute right-0 top-12 w-48 rounded-xl border border-white/10 bg-[#111111] p-2 shadow-2xl shadow-black/40">
                  <Link
                    href="/profile"
                    onClick={() => setProfileMenuOpen(false)}
                    className="block rounded-lg px-3 py-2 text-sm text-white/75 transition hover:bg-white/10 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
                  >
                    View profile
                  </Link>
                  <button
                    type="button"
                    onClick={handleSignOut}
                    className="mt-1 flex w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-[#ff8b92] transition hover:bg-[#E50914]/15 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
                  >
                    Sign Out
                  </button>
                </div>
              ) : null}
            </div>
          ) : (
            <>
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
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
