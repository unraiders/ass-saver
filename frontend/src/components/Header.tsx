import { ThemeToggle } from "@/components/ThemeToggle";

export function Header() {
  return (
    <header className="relative flex flex-col items-center pt-10 pb-4">
      {/* Logo y toggle anclados a los extremos del viewport (no al contenedor) */}
      <img
        src="/ass-saver-logo.png"
        alt="ASS-SAVER"
        className="fixed left-6 top-5 h-16 w-16"
      />
      <div className="fixed right-6 top-6">
        <ThemeToggle />
      </div>
      <h1 className="text-4xl font-bold tracking-tight">ASS-SAVER</h1>
      <p className="mt-2 text-center text-lg text-muted-foreground">
        La marca de agua en tus imágenes (png, jpg)
      </p>
    </header>
  );
}
