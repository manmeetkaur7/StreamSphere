"use client";

import { type FormEvent, useState } from "react";

export default function ForgotPasswordForm() {
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const email = String(new FormData(event.currentTarget).get("email") ?? "").trim();

    if (!email) {
      setError("Enter your email address.");
      setSubmitted(false);
    } else if (!/^\S+@\S+\.\S+$/.test(email)) {
      setError("Enter a valid email address.");
      setSubmitted(false);
    } else {
      setError("");
      setSubmitted(true);
    }
  };

  return (
    <form className="space-y-5" onSubmit={handleSubmit} noValidate>
      <div>
        <label htmlFor="forgot-email" className="mb-2 block text-sm font-medium text-white/80">Email address</label>
        <input id="forgot-email" name="email" type="email" autoComplete="email" aria-invalid={Boolean(error)} aria-describedby={error ? "forgot-email-error" : submitted ? "forgot-success" : undefined} className="h-12 w-full rounded-lg border border-white/15 bg-black/20 px-4 text-sm text-white outline-none transition-colors placeholder:text-white/30 focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/20" placeholder="you@example.com" />
        {error && <p id="forgot-email-error" className="mt-2 text-xs text-red-300">{error}</p>}
        {submitted && <p id="forgot-success" className="mt-2 text-xs text-emerald-300">If an account exists, recovery instructions are ready to be sent.</p>}
      </div>
      <button type="submit" className="h-12 w-full rounded-lg bg-[#E50914] text-sm font-semibold text-white transition-all hover:-translate-y-0.5 hover:bg-[#b80710] hover:shadow-[0_12px_28px_rgba(229,9,20,0.3)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914]">Send Reset Link</button>
      <a href="/login" className="block text-center text-sm text-white/60 transition-colors hover:text-white">Back to sign in</a>
    </form>
  );
}
