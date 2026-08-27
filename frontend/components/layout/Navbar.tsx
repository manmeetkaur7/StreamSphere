"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import NotificationCenter from "@/components/layout/NotificationCenter";
import { clearAccessToken, getAccessToken } from "@/lib/auth";
import type { Profile } from "@/lib/catalog";
import { fetchWithAuth } from "@/lib/auth";

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

  useEffect(() => {
    let active = true;
    const token = getAccessToken();

    if (!token) {
      return;
    }

    void fetchWithAuth<Profile>("/profile")
      .then((payload) => {
        if (!active) {
          return;
        }
        setProfile(payload);
      })
      .catch((error) => {
        if (!active) {
          return;
        }
        if (error instanceof Error && error.message.includes("Could not validate credentials")) {
          clearAccessToken();
          setAuthenticated(false);
          setProfile(null);
        }
      });

    return () => {
      active = false;
    };
  }, []);

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
          <Link
            href="/profile"
            aria-label="Open user profile"
            className="flex h-9 w-9 items-center justify-center rounded-full border border-white/20 bg-gradient-to-br from-[#E50914] to-[#7f0710] text-xs font-semibold uppercase text-white transition-transform hover:scale-105 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]"
          >
            {(profile?.username ?? "SS").slice(0, 2)}
          </Link>
          {!authenticated ? (
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
          ) : null}
        </div>
      </nav>
    </header>
  );
}
