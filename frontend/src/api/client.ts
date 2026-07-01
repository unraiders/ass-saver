// Cliente de la API. En dev, Vite proxya /api a FastAPI (localhost:8000);
// en producción todo sale del mismo origen.

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`Error ${res.status} en ${path}`);
  }
  return res.json() as Promise<T>;
}

export interface WatermarkPayload {
  image: string;
  text: string;
  font_size: number;
  opacity: number;
  watermark_type: string;
  text_angle: number;
  color_mode: string;
}

export interface WatermarkResponse {
  success: boolean;
  image: string;
  message: string;
}

export const api = {
  watermark: (payload: WatermarkPayload) =>
    post<WatermarkResponse>("/api/watermark", payload),
};
