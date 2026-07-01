import { create } from "zustand";
import { toast } from "sonner";
import { api } from "@/api/client";

export type WatermarkType = "Texto lineal" | "Texto cruzado";
export type ColorMode = "Actual" | "Escala de grises";

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

  // Acciones.
  handleFile: (file: File) => Promise<void>;
  loadTestFile: (path: string) => Promise<void>;
  applyWatermark: () => Promise<void>;
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

export const useAppStore = create<AppState>((set, get) => ({
  image: "",
  resultImage: "",
  watermarkText: "",
  fontSize: 16,
  opacity: 125,
  watermarkType: "Texto lineal",
  textAngle: 0,
  colorMode: "Actual",
  isLoadingFile: false,
  isLoadingWatermark: false,

  setWatermarkText: (v) => set({ watermarkText: v }),
  setFontSize: (v) => set({ fontSize: v }),
  setOpacity: (v) => set({ opacity: v }),
  setWatermarkType: (v) =>
    // Al cambiar a un tipo que no es lineal, el ángulo pierde sentido: se fija a 45.
    set(v === "Texto lineal" ? { watermarkType: v } : { watermarkType: v, textAngle: 45 }),
  setTextAngle: (v) => set({ textAngle: v }),
  setColorMode: (v) => set({ colorMode: v }),

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
    } catch {
      toast.error("Error al cargar el archivo");
    } finally {
      set({ isLoadingFile: false });
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
    } catch {
      toast.error("Error al cargar el archivo de prueba");
    } finally {
      set({ isLoadingFile: false });
    }
  },

  applyWatermark: async () => {
    const s = get();
    if (!s.image || !s.watermarkText.trim()) {
      toast.error("Por favor, sube una imagen y escribe un texto para la marca de agua.");
      return;
    }
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
      });
      if (resp.success) {
        set({ resultImage: resp.image });
        toast.success(
          "¡Marca de agua aplicada con éxito!, solo necesitas descargarla para salvar tú culo!!"
        );
      } else {
        toast.error(resp.message || "No se pudo aplicar la marca de agua.");
      }
    } catch {
      toast.error("Error al procesar la imagen.");
    } finally {
      set({ isLoadingWatermark: false });
    }
  },

  reset: () =>
    set({
      image: "",
      resultImage: "",
      watermarkText: "",
      colorMode: "Actual",
      isLoadingFile: false,
      isLoadingWatermark: false,
    }),
}));
