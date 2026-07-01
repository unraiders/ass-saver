import { useCallback, useRef, useState } from "react";
import { Loader2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Slider } from "@/components/ui/slider";
import {
  useAppStore,
  type ColorMode,
  type WatermarkType,
} from "@/store/useAppStore";

const ANGLES = [0, 45, 90, 180];
const DOWNLOAD_NAME = "save-your-ass_watermarked.png";

// Convierte una data-URL a Blob de forma síncrona (para no perder el gesto de
// usuario que exige la Web Share API en iOS).
function dataUrlToBlob(dataUrl: string): Blob {
  const [header, base64] = dataUrl.split(",");
  const mime = header.match(/:(.*?);/)?.[1] ?? "image/png";
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: mime });
}

function isMobile(): boolean {
  return /iphone|ipad|ipod|android/i.test(navigator.userAgent);
}

// Descarga clásica por enlace (funciona en escritorio).
function anchorDownload(blob: Blob) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = DOWNLOAD_NAME;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Guarda/descarga la imagen resultante según la plataforma:
//  - Escritorio: descarga directa por enlace.
//  - Móvil con Web Share (HTTPS): hoja nativa con "Guardar imagen".
//  - Móvil sin Web Share (p. ej. HTTP en LAN): abre la imagen en otra pestaña
//    para poder mantenerla pulsada y "Guardar en Fotos".
function downloadResult(dataUrl: string) {
  const blob = dataUrlToBlob(dataUrl);

  if (!isMobile()) {
    anchorDownload(blob);
    return;
  }

  const file = new File([blob], DOWNLOAD_NAME, { type: blob.type });
  const nav = navigator as Navigator & {
    canShare?: (data: { files: File[] }) => boolean;
    share?: (data: { files: File[]; title?: string }) => Promise<void>;
  };

  if (nav.canShare && nav.share && nav.canShare({ files: [file] })) {
    nav.share({ files: [file], title: DOWNLOAD_NAME }).catch(() => {
      /* el usuario canceló el diálogo de compartir */
    });
    return;
  }

  const url = URL.createObjectURL(blob);
  window.open(url, "_blank");
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}

export function WatermarkForm() {
  const {
    image,
    resultImage,
    watermarkText,
    fontSize,
    opacity,
    watermarkType,
    textAngle,
    colorMode,
    isLoadingFile,
    isLoadingWatermark,
    setWatermarkText,
    setFontSize,
    setOpacity,
    setWatermarkType,
    setTextAngle,
    setColorMode,
    handleFile,
    loadTestFile,
    applyWatermark,
    reset,
  } = useAppStore();

  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const angleDisabled = watermarkType !== "Texto lineal";

  return (
    <Card>
      <CardContent className="space-y-6">
        {/* Cabecera con botón limpiar */}
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-sm font-medium text-muted-foreground">
            Sube una imagen y personaliza tu marca de agua
          </h2>
          <Button variant="outline" size="sm" onClick={reset}>
            Limpiar
          </Button>
        </div>

        {/* Zona de subida */}
        <div
          className={`flex flex-col items-center gap-3 rounded-lg border-2 border-dashed p-8 transition-colors ${
            dragging ? "border-primary bg-accent/40" : "border-input"
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
        >
          <p className="text-center text-sm text-muted-foreground">
            Arrastra una imagen aquí o haz clic para seleccionar
          </p>
          <input
            ref={inputRef}
            type="file"
            accept=".png,.jpg,.jpeg"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
              e.target.value = "";
            }}
          />
          <Button
            onClick={() => inputRef.current?.click()}
            disabled={isLoadingFile}
          >
            {isLoadingFile ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" /> Cargando Archivo..
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" /> Seleccionar Archivo
              </>
            )}
          </Button>
          <button
            type="button"
            onClick={() => loadTestFile("/dni_ficticio.jpg")}
            className="mt-1 rounded-full border border-input px-3 py-1 text-xs text-muted-foreground transition-colors hover:bg-accent"
          >
            Cargar fichero de prueba
          </button>
        </div>

        {/* Preview de la imagen cargada */}
        {image && (
          <div className="flex justify-center">
            <img
              src={image}
              alt="Imagen cargada"
              className="max-h-72 rounded-md border"
            />
          </div>
        )}

        {/* Texto de la marca de agua */}
        <div className="space-y-1.5">
          <Label htmlFor="wm-text">Texto para la marca de agua</Label>
          <Input
            id="wm-text"
            placeholder="Texto para la marca de agua"
            value={watermarkText}
            onChange={(e) => setWatermarkText(e.target.value)}
          />
          <p className="text-xs font-light text-muted-foreground">
            Ejemplo: SOLO VÁLIDO PARA DAR DE BAJA MOVISTAR LA LIGA.
          </p>
        </div>

        {/* Tamaño de fuente */}
        <div className="space-y-2">
          <Label>Tamaño de fuente: {fontSize}</Label>
          <Slider
            min={10}
            max={100}
            step={2}
            value={[fontSize]}
            onValueChange={(v) => setFontSize(v[0])}
          />
        </div>

        {/* Opacidad */}
        <div className="space-y-2">
          <Label>Opacidad: {opacity}</Label>
          <Slider
            min={0}
            max={255}
            step={5}
            value={[opacity]}
            onValueChange={(v) => setOpacity(v[0])}
          />
        </div>

        {/* Modo de color */}
        <div className="space-y-2">
          <Label>Modo de color:</Label>
          <RadioGroup
            value={colorMode}
            onValueChange={(v) => setColorMode(v as ColorMode)}
          >
            {(["Actual", "Escala de grises"] as ColorMode[]).map((opt) => (
              <div key={opt} className="flex items-center gap-2">
                <RadioGroupItem value={opt} id={`color-${opt}`} />
                <Label htmlFor={`color-${opt}`} className="font-normal">
                  {opt}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>

        {/* Tipo de disposición */}
        <div className="space-y-2">
          <Label>Tipo de disposición de la marca de agua:</Label>
          <RadioGroup
            value={watermarkType}
            onValueChange={(v) => setWatermarkType(v as WatermarkType)}
          >
            {(["Texto lineal", "Texto cruzado"] as WatermarkType[]).map((opt) => (
              <div key={opt} className="flex items-center gap-2">
                <RadioGroupItem value={opt} id={`type-${opt}`} />
                <Label htmlFor={`type-${opt}`} className="font-normal">
                  {opt}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>

        {/* Inclinación (solo texto lineal) */}
        <div className={`space-y-2 ${angleDisabled ? "opacity-50" : ""}`}>
          <Label>Inclinación del texto:</Label>
          <RadioGroup
            value={String(textAngle)}
            onValueChange={(v) => setTextAngle(Number(v))}
            disabled={angleDisabled}
            className="flex gap-4"
          >
            {ANGLES.map((a) => (
              <div key={a} className="flex items-center gap-2">
                <RadioGroupItem value={String(a)} id={`angle-${a}`} />
                <Label htmlFor={`angle-${a}`} className="font-normal">
                  {a}°
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>

        {/* Aplicar */}
        <Button
          className="w-full"
          onClick={applyWatermark}
          disabled={isLoadingWatermark}
        >
          {isLoadingWatermark ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Aplicando Marca de Agua...
            </>
          ) : (
            "Aplicar Marca de Agua"
          )}
        </Button>

        {/* Resultado */}
        {resultImage && (
          <div className="flex flex-col items-center gap-3 border-t pt-6">
            <img
              src={resultImage}
              alt="Resultado con marca de agua"
              className="max-h-80 rounded-md border"
            />
            <Button className="w-full" onClick={() => downloadResult(resultImage)}>
              Descargar Imagen
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
