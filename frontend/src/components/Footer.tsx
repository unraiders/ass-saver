import { Heart } from "lucide-react";

const VERSION = import.meta.env.VITE_APP_VERSION ?? "dev";

export function Footer() {
  return (
    <footer className="mt-2 flex items-center justify-center gap-1.5 py-2 text-sm text-muted-foreground">
      <span>ASS-SAVER - Desarrollado con</span>
      <Heart size={14} className="fill-red-500 text-red-500" />
      <span>Versión {VERSION}</span>
    </footer>
  );
}
