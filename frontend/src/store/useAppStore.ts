import { create } from "zustand";
import { toast } from "sonner";
import { api } from "@/api/client";

export type WatermarkType = "Texto lineal" | "Texto cruzado";
export type ColorMode = "Actual" | "Escala de grises";

// Fuentes agrupadas por estilo. Los nombres deben coincidir con las claves de
// `FONTS` del backend. La de por defecto es "DejaVu Sans Mono" (ver estado inicial).
export const FONT_GROUPS = [
  { label: "Sans serif", fonts: ["DejaVu Sans", "Open Sans", "Montserrat"] },
  { label: "Con serifa", fonts: ["DejaVu Serif", "PT Serif"] },
  { label: "Monoespaciada", fonts: ["DejaVu Sans Mono"] },
  { label: "Impacto", fonts: ["DejaVu Sans Bold", "Oswald", "Anton"] },
] as const;

export type FontFamily = (typeof FONT_GROUPS)[number]["fonts"][number];

// Lista plana derivada de los grupos (p. ej. para validación).
export const FONT_FAMILIES = FONT_GROUPS.flatMap(
  (g) => g.fonts
) as FontFamily[];

// Posiciones para logo y sello: cuatro esquinas o centro.
export const POSITIONS = [
  "top-left",
  "top-right",
  "center",
  "bottom-left",
  "bottom-right",
] as const;
export type Position = (typeof POSITIONS)[number];

interface AppState {
  // Imagen origen (data-URL base64) y resultado.
  image: string;
  resultImage: string;

  // Parámetros de la marca de agua.
  watermarkText: string;
  fontSize: number;
  opacity: number;
  watermarkType: WatermarkType;
  textAngle: number;
  colorMode: ColorMode;
  color: string;
  fontFamily: FontFamily;

  // Logo opcional.
  logo: string;
  logoScale: number;
  logoOpacity: number;
  logoPosition: Position;

  // Sello de fecha.
  addDate: boolean;
  stampPosition: Position;

  // Estados de carga.
  isLoadingFile: boolean;
  isLoadingWatermark: boolean;

  // Setters.
  setWatermarkText: (v: string) => void;
  setFontSize: (v: number) => void;
  setOpacity: (v: number) => void;
  setWatermarkType: (v: WatermarkType) => void;
  setTextAngle: (v: number) => void;
  setColorMode: (v: ColorMode) => void;
  setColor: (v: string) => void;
  setFontFamily: (v: FontFamily) => void;
  setLogoScale: (v: number) => void;
  setLogoOpacity: (v: number) => void;
  setLogoPosition: (v: Position) => void;
  setAddDate: (v: boolean) => void;
  setStampPosition: (v: Position) => void;
  clearLogo: () => void;

  // Acciones.
  handleFile: (file: File) => Promise<void>;
  handleLogoFile: (file: File) => Promise<void>;
  loadTestFile: (path: string) => Promise<void>;
  applyWatermark: (silent?: boolean) => Promise<void>;
  applyWatermarkDebounced: () => void;
  reset: () => void;
}

const ACCEPTED = ["image/png", "image/jpeg"];

function fileToDataUrl(file: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

// Estado del debounce y guardas de la vista previa en vivo.
let previewTimer: ReturnType<typeof setTimeout> | undefined;
let previewSeq = 0;
const PREVIEW_DELAY_MS = 400;

export const useAppStore = create<AppState>((set, get) => {
  // Dispara la vista previa con debounce tras cambiar un parámetro.
  const triggerPreview = () => get().applyWatermarkDebounced();

  return {
    image: "",
    resultImage: "",
    watermarkText: "",
    fontSize: 16,
    opacity: 125,
    watermarkType: "Texto lineal",
    textAngle: 0,
    colorMode: "Actual",
    color: "#808080",
    fontFamily: "DejaVu Sans Mono",
    logo: "",
    logoScale: 25,
    logoOpacity: 128,
    logoPosition: "center",
    addDate: false,
    stampPosition: "bottom-right",
    isLoadingFile: false,
    isLoadingWatermark: false,

    setWatermarkText: (v) => {
      set({ watermarkText: v });
      triggerPreview();
    },
    setFontSize: (v) => {
      set({ fontSize: v });
      triggerPreview();
    },
    setOpacity: (v) => {
      set({ opacity: v });
      triggerPreview();
    },
    setWatermarkType: (v) => {
      // Al cambiar a un tipo que no es lineal, el ángulo pierde sentido: se fija a 45.
      set(
        v === "Texto lineal"
          ? { watermarkType: v }
          : { watermarkType: v, textAngle: 45 }
      );
      triggerPreview();
    },
    setTextAngle: (v) => {
      set({ textAngle: v });
      triggerPreview();
    },
    setColorMode: (v) => {
      set({ colorMode: v });
      triggerPreview();
    },
    setColor: (v) => {
      set({ color: v });
      triggerPreview();
    },
    setFontFamily: (v) => {
      set({ fontFamily: v });
      triggerPreview();
    },
    setLogoScale: (v) => {
      set({ logoScale: v });
      triggerPreview();
    },
    setLogoOpacity: (v) => {
      set({ logoOpacity: v });
      triggerPreview();
    },
    setLogoPosition: (v) => {
      set({ logoPosition: v });
      triggerPreview();
    },
    setAddDate: (v) => {
      set({ addDate: v });
      triggerPreview();
    },
    setStampPosition: (v) => {
      set({ stampPosition: v });
      triggerPreview();
    },
    clearLogo: () => {
      set({ logo: "" });
      triggerPreview();
    },

    handleFile: async (file) => {
      if (!ACCEPTED.includes(file.type)) {
        toast.error("Formato no válido. Usa una imagen .png o .jpg.");
        return;
      }
      set({ isLoadingFile: true });
      try {
        const dataUrl = await fileToDataUrl(file);
        set({ image: dataUrl, resultImage: "" });
        toast.success("Archivo cargado correctamente");
        triggerPreview();
      } catch {
        toast.error("Error al cargar el archivo");
      } finally {
        set({ isLoadingFile: false });
      }
    },

    handleLogoFile: async (file) => {
      if (!ACCEPTED.includes(file.type)) {
        toast.error("Formato de logo no válido. Usa una imagen .png o .jpg.");
        return;
      }
      try {
        const dataUrl = await fileToDataUrl(file);
        set({ logo: dataUrl });
        toast.success("Logo cargado correctamente");
        triggerPreview();
      } catch {
        toast.error("Error al cargar el logo");
      }
    },

    loadTestFile: async (path) => {
      set({ isLoadingFile: true });
      try {
        const res = await fetch(path);
        if (!res.ok) throw new Error("no encontrado");
        const blob = await res.blob();
        const dataUrl = await fileToDataUrl(blob);
        set({ image: dataUrl, resultImage: "" });
        toast.success("Archivo de prueba cargado correctamente");
        triggerPreview();
      } catch {
        toast.error("Error al cargar el archivo de prueba");
      } finally {
        set({ isLoadingFile: false });
      }
    },

    // Vista previa en vivo: reprograma la aplicación de la marca con debounce.
    applyWatermarkDebounced: () => {
      const s = get();
      if (!s.image || !s.watermarkText.trim()) return;
      if (previewTimer) clearTimeout(previewTimer);
      previewTimer = setTimeout(() => {
        void get().applyWatermark(true);
      }, PREVIEW_DELAY_MS);
    },

    // `silent` = vista previa automática: sin toasts para no saturar al usuario.
    applyWatermark: async (silent = false) => {
      const s = get();
      if (!s.image || !s.watermarkText.trim()) {
        if (!silent) {
          toast.error(
            "Por favor, sube una imagen y escribe un texto para la marca de agua."
          );
        }
        return;
      }
      const seq = ++previewSeq;
      set({ isLoadingWatermark: true });
      try {
        const resp = await api.watermark({
          image: s.image,
          text: s.watermarkText,
          font_size: s.fontSize,
          opacity: s.opacity,
          watermark_type: s.watermarkType,
          text_angle: s.textAngle,
          color_mode: s.colorMode,
          color: s.color,
          font_family: s.fontFamily,
          logo: s.logo,
          logo_scale: s.logoScale,
          logo_opacity: s.logoOpacity,
          logo_position: s.logoPosition,
          stamp_text: s.addDate
            ? new Date().toLocaleDateString("es-ES")
            : "",
          stamp_position: s.stampPosition,
        });
        // Ignorar respuestas obsoletas (llegó una petición más reciente).
        if (seq !== previewSeq) return;
        if (resp.success) {
          set({ resultImage: resp.image });
          if (!silent) {
            toast.success(
              "¡Marca de agua aplicada con éxito!, solo necesitas descargarla para salvar tú culo!!"
            );
          }
        } else if (!silent) {
          toast.error(resp.message || "No se pudo aplicar la marca de agua.");
        }
      } catch {
        if (!silent) toast.error("Error al procesar la imagen.");
      } finally {
        if (seq === previewSeq) set({ isLoadingWatermark: false });
      }
    },

    reset: () => {
      if (previewTimer) clearTimeout(previewTimer);
      previewSeq++;
      set({
        image: "",
        resultImage: "",
        watermarkText: "",
        colorMode: "Actual",
        color: "#808080",
        fontFamily: "DejaVu Sans Mono",
        logo: "",
        logoScale: 25,
        logoOpacity: 128,
        logoPosition: "center",
        addDate: false,
        stampPosition: "bottom-right",
        isLoadingFile: false,
        isLoadingWatermark: false,
      });
    },
  };
});
