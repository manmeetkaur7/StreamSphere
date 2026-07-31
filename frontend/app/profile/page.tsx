import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";
import ProfileDashboard from "@/components/profile/ProfileDashboard";

export default function ProfilePage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 pb-16 pt-28 sm:px-8 lg:px-10 lg:pb-24 lg:pt-32">
        <section className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-[#E50914]">Profile</p>
          <div className="max-w-2xl">
            <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">Your StreamSphere profile</h1>
            <p className="mt-3 text-base leading-7 text-white/65">
              Review your saved titles, recent reviews, and personal activity across the catalog.
            </p>
          </div>
        </section>
        <ProfileDashboard />
      </main>
      <Footer />
    </div>
  );
}
