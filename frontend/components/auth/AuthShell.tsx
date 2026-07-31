import type { ReactNode } from "react";
import Navbar from "@/components/layout/Navbar";

interface AuthShellProps {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
  footer: ReactNode;
}

export default function AuthShell({
  eyebrow,
  title,
  description,
  children,
  footer,
}: AuthShellProps) {
  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <Navbar />
      <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 pb-16 pt-32 sm:px-8">
        <div aria-hidden="true" className="absolute left-1/2 top-1/3 h-[32rem] w-[32rem] -translate-x-1/2 rounded-full bg-[#E50914]/10 blur-3xl" />
        <div aria-hidden="true" className="absolute inset-0 bg-[linear-gradient(135deg,rgba(229,9,20,0.08),transparent_35%,rgba(255,255,255,0.03)_100%)]" />
        <section className="relative z-10 w-full max-w-md rounded-2xl border border-white/10 bg-white/[0.07] p-6 shadow-2xl shadow-black/50 backdrop-blur-2xl sm:p-9" aria-labelledby="auth-title">
          <div className="mb-8 text-center">
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.28em] text-[#E50914]">{eyebrow}</p>
            <h1 id="auth-title" className="text-3xl font-semibold tracking-tight text-white">{title}</h1>
            <p className="mt-3 text-sm leading-6 text-white/55">{description}</p>
          </div>
          {children}
          <div className="mt-7 text-center text-sm text-white/50">{footer}</div>
        </section>
      </main>
    </div>
  );
}
