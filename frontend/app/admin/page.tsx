import AdminDashboard from "@/components/admin/AdminDashboard";
import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";

export default function AdminPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 pb-16 pt-28 sm:px-8 lg:px-10 lg:pb-24 lg:pt-32">
        <section className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-[#E50914]">Admin</p>
          <div className="max-w-3xl">
            <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">Platform oversight and moderation</h1>
            <p className="mt-3 text-base leading-7 text-white/65">
              Review platform health, user activity, recent catalog changes, and moderation actions from one place.
            </p>
          </div>
        </section>
        <AdminDashboard />
      </main>
      <Footer />
    </div>
  );
}
