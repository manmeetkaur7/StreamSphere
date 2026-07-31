"use client";

import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { registerAndLogin } from "@/lib/auth";

interface RegisterErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  form?: string;
}

function PasswordToggle({ visible, onToggle, label }: { visible: boolean; onToggle: () => void; label: string }) {
  return (
    <button type="button" aria-label={visible ? `Hide ${label}` : `Show ${label}`} onClick={onToggle} className="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-white/45 transition-colors hover:text-white focus-visible:outline-2 focus-visible:outline-[#E50914]">
      <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
        {visible ? <><path strokeLinecap="round" strokeLinejoin="round" d="M2.46 12S5.82 5 12 5s9.54 7 9.54 7S18.18 19 12 19s-9.54-7-9.54-7Z" /><circle cx="12" cy="12" r="2.5" /></> : <><path strokeLinecap="round" strokeLinejoin="round" d="M3 3l18 18M10.58 10.58a2 2 0 0 0 2.83 2.83M9.88 4.24A9.5 9.5 0 0 1 12 4c5.5 0 9 5 9 8a8.7 8.7 0 0 1-2.1 3.92M6.61 6.61C4.4 8.1 3 10.13 3 12c0 3 3.5 8 9 8 1.2 0 2.3-.27 3.27-.7" /></>}
      </svg>
    </button>
  );
}

function SocialButtons() {
  return (
    <div className="space-y-3">
      <button type="button" className="flex h-12 w-full items-center justify-center gap-3 rounded-lg border border-white/15 bg-white/5 text-sm font-medium text-white transition-all hover:-translate-y-0.5 hover:border-white/30 hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"><span className="font-bold text-[#4285F4]">G</span>Continue with Google</button>
      <button type="button" className="flex h-12 w-full items-center justify-center gap-3 rounded-lg border border-white/15 bg-white/5 text-sm font-medium text-white transition-all hover:-translate-y-0.5 hover:border-white/30 hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"><span className="text-lg font-bold">◉</span>Continue with GitHub</button>
    </div>
  );
}

const inputClass = "h-12 w-full rounded-lg border border-white/15 bg-black/20 px-4 text-sm text-white outline-none transition-colors placeholder:text-white/30 focus:border-[#E50914] focus:ring-2 focus:ring-[#E50914]/20";

export default function RegisterForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<RegisterErrors>({});
  const router = useRouter();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const username = String(data.get("username") ?? "").trim();
    const email = String(data.get("email") ?? "").trim();
    const password = String(data.get("password") ?? "");
    const confirmPassword = String(data.get("confirmPassword") ?? "");
    const nextErrors: RegisterErrors = {};

    if (!username) nextErrors.username = "Enter a username.";
    else if (!/^[a-zA-Z0-9_]+$/.test(username)) nextErrors.username = "Use letters, numbers, or underscores only.";
    if (!email) nextErrors.email = "Enter your email address.";
    else if (!/^\S+@\S+\.\S+$/.test(email)) nextErrors.email = "Enter a valid email address.";
    if (password.length < 8) nextErrors.password = "Password must be at least 8 characters.";
    if (confirmPassword !== password) nextErrors.confirmPassword = "Passwords do not match.";
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    try {
      setIsSubmitting(true);
      await registerAndLogin(username, email, password);
      router.push("/profile");
      router.refresh();
    } catch (error) {
      setErrors({ form: error instanceof Error ? error.message : "Unable to create account." });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <SocialButtons />
      <div className="my-6 flex items-center gap-4 text-xs uppercase tracking-widest text-white/30"><span className="h-px flex-1 bg-white/10" />or<span className="h-px flex-1 bg-white/10" /></div>
      <form className="space-y-4" onSubmit={handleSubmit} noValidate>
        <div><label htmlFor="register-username" className="mb-2 block text-sm font-medium text-white/80">Username</label><input id="register-username" name="username" type="text" autoComplete="username" aria-invalid={Boolean(errors.username)} className={inputClass} placeholder="alex_morgan" />{errors.username && <p className="mt-2 text-xs text-red-300">{errors.username}</p>}</div>
        <div><label htmlFor="register-email" className="mb-2 block text-sm font-medium text-white/80">Email address</label><input id="register-email" name="email" type="email" autoComplete="email" aria-invalid={Boolean(errors.email)} className={inputClass} placeholder="you@example.com" />{errors.email && <p className="mt-2 text-xs text-red-300">{errors.email}</p>}</div>
        <div><label htmlFor="register-password" className="mb-2 block text-sm font-medium text-white/80">Password</label><div className="relative"><input id="register-password" name="password" type={showPassword ? "text" : "password"} autoComplete="new-password" aria-invalid={Boolean(errors.password)} className={`${inputClass} pr-12`} placeholder="At least 8 characters" /><PasswordToggle visible={showPassword} onToggle={() => setShowPassword(!showPassword)} label="password" /></div>{errors.password && <p className="mt-2 text-xs text-red-300">{errors.password}</p>}</div>
        <div><label htmlFor="register-confirm-password" className="mb-2 block text-sm font-medium text-white/80">Confirm password</label><div className="relative"><input id="register-confirm-password" name="confirmPassword" type={showConfirmPassword ? "text" : "password"} autoComplete="new-password" aria-invalid={Boolean(errors.confirmPassword)} className={`${inputClass} pr-12`} placeholder="Repeat your password" /><PasswordToggle visible={showConfirmPassword} onToggle={() => setShowConfirmPassword(!showConfirmPassword)} label="confirm password" /></div>{errors.confirmPassword && <p className="mt-2 text-xs text-red-300">{errors.confirmPassword}</p>}</div>
        <label className="flex items-start gap-2 pt-1 text-xs leading-5 text-white/55"><input name="terms" type="checkbox" required className="mt-1 h-4 w-4 rounded border-white/20 bg-black/20 accent-[#E50914]" />I agree to the StreamSphere terms and privacy policy.</label>
        {errors.form && <p className="text-sm text-red-300">{errors.form}</p>}
        <button type="submit" disabled={isSubmitting} className="h-12 w-full rounded-lg bg-[#E50914] text-sm font-semibold text-white transition-all hover:-translate-y-0.5 hover:bg-[#b80710] hover:shadow-[0_12px_28px_rgba(229,9,20,0.3)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#E50914] disabled:cursor-not-allowed disabled:opacity-60">{isSubmitting ? "Creating Account..." : "Create Account"}</button>
      </form>
    </>
  );
}
