import { Toaster } from "sonner";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { WatermarkForm } from "@/components/WatermarkForm";

export default function App() {
  const isDark = document.documentElement.classList.contains("dark");

  return (
    <div className="min-h-screen bg-background">
      <Toaster position="top-center" theme={isDark ? "dark" : "light"} richColors />
      <div className="mx-auto w-full max-w-2xl px-4 pb-10">
        <Header />
        <WatermarkForm />
        <Footer />
      </div>
    </div>
  );
}
