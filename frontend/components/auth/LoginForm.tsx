"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { loginWithCredentials } from "@/lib/auth";

interface LoginErrors {
  identifier?: string;
  password?: string;
  form?: string;
}

function EyeIcon({ hidden }: { hidden: boolean }) {
  return hidden ? (
    <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 3l18 18M10.58 10.58a2 2 0 0 0 2.83 2.83M9.88 4.24A9.5 9.5 0 0 1 12 4c5.5 0 9 5 9 8a8.7 8.7 0 0 1-2.1 3.92M6.61 6.61C4.4 8.1 3 10.13 3 12c0 3 3.5 8 9 8 1.2 0 2.3-.27 3.27-.7" />
    </svg>
  ) : (
    <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.46 12S5.82 5 12 5s9.54 7 9.54 7S18.18 19 12 19s-9.54-7-9.54-7Z" />
      <circle cx="12" cy="12" r="2.5" />
    </svg>
  );
}

function SocialButtons() {
  return (
    <div className="space-y-3">
      <button type="button" className="flex h-12 w-full items-center justify-center gap-3 rounded-lg border border-white/15 bg-white/5 text-sm font-medium text-white transition-all hover:-translate-y-0.5 hover:border-white/30 hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
        <span className="text-base font-bold text-[#4285F4]">G</span>
        Continue with Google
      </button>
      <button type="button" className="flex h-12 w-full items-center justify-center gap-3 rounded-lg border border-white/15 bg-white/5 text-sm font-medium text-white transition-all hover:-translate-y-0.5 hover:border-white/30 hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
        <span className="text-lg font-bold">◉</span>
        Continue with GitHub
      </button>
    </div>
  );
}

export default function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<LoginErrors>({});
  const router = useRouter();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const identifier = String(formData.get("identifier") ?? "").trim();
    const password = String(formData.get("password") ?? "");
    const nextErrors: LoginErrors = {};

    if (!identifier) nextErrors.identifier = "Enter your email or username.";
    if (!password) nextErrors.password = "Enter your password.";
    else if (password.length < 8) nextErrors.password = "Password must be at least 8 characters.";
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    try {
      setIsSubmitting(true);
      await loginWithCredentials(identifier, password);
      router.push("/profile");
      router.refresh();
    } catch (error) {
      setErrors({ form: error instanceof Error ? error.message : "Unable to sign in." });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <SocialButtons />
      <div className="my-6 flex items-center gap-4 text-xs uppercase tracking-widest text-white/30">
        <span className="h-px flex-1 bg-white/10" />
        or
        <span className="h-px flex-1 bg-white/10" />
      </div>
      <form className="space-y-5" onSubmit={handleSubmit} noValidate>
        <div>
          <label htmlFor="login-identifier" className="mb-2 block text-sm font-medium text-white/80">Email or username</label>
          <input id="login-identifier" name="identifier" type="text" autoComplete="username" aria-invalid={Boolean(errors.identifier)} aria-describedby={errors.identifier ? "login-identifier-error" : undefined} className="h-12 w-full rounded-lg border border-white/15 bg-black/20 px-4 text-sm text-white outline-none transition-colors placeholder:text-white/30 focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/20" placeholder="you@example.com" />
          {errors.identifier && <p id="login-identifier-error" className="mt-2 text-xs text-red-300">{errors.identifier}</p>}
        </div>
        <div>
          <label htmlFor="login-password" className="mb-2 block text-sm font-medium text-white/80">Password</label>
          <div className="relative">
            <input id="login-password" name="password" type={showPassword ? "text" : "password"} autoComplete="current-password" aria-invalid={Boolean(errors.password)} aria-describedby={errors.password ? "login-password-error" : undefined} className="h-12 w-full rounded-lg border border-white/15 bg-black/20 px-4 pr-12 text-sm text-white outline-none transition-colors placeholder:text-white/30 focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/20" placeholder="Enter your password" />
            <button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-white/45 transition-colors hover:text-white focus-visible:outline-2 focus-visible:outline-[#E50914]"><EyeIcon hidden={!showPassword} /></button>
          </div>
          {errors.password && <p id="login-password-error" className="mt-2 text-xs text-red-300">{errors.password}</p>}
        </div>
        <div className="flex items-center justify-between gap-4 text-sm">
          <label className="flex items-center gap-2 text-white/60"><input name="remember" type="checkbox" className="h-4 w-4 rounded border-white/20 bg-black/20 accent-[#E50914]" />Remember me</label>
          <Link href="/forgot-password" className="text-[#ff5962] transition-colors hover:text-white">Forgot password?</Link>
        </div>
        {errors.form && <p className="text-sm text-red-300">{errors.form}</p>}
        <button type="submit" disabled={isSubmitting} className="h-12 w-full rounded-lg bg-[#E50914] text-sm font-semibold text-white transition-all hover:-translate-y-0.5 hover:bg-[#b80710] hover:shadow-[0_12px_28px_rgba(229,9,20,0.3)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914] disabled:cursor-not-allowed disabled:opacity-60">{isSubmitting ? "Signing In..." : "Sign In"}</button>
      </form>
    </>
  );
}
