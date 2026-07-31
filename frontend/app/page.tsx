import HomeExperience from "@/components/home/HomeExperience";
import Footer from "@/components/layout/Footer";
import Hero from "@/components/home/Hero";
import Navbar from "@/components/layout/Navbar";

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <main>
        <Hero />
        <HomeExperience />
      </main>
      <Footer />
    </div>
  );
}
