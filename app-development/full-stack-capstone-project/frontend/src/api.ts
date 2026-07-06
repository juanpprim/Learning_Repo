// Typed API client. These types MIRROR backend/app/schemas.py by hand —
// keep them in sync when the contract changes (codegen is a Tier C nicety).

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface HouseFeatures {
  area: number;
  bedrooms: number;
  bathrooms: number;
  stories: number;
  mainroad: boolean;
  guestroom: boolean;
  basement: boolean;
  hotwaterheating: boolean;
  airconditioning: boolean;
  parking: number;
  prefarea: boolean;
  furnishingstatus: "furnished" | "semi-furnished" | "unfurnished";
}

export type ModelName = "linreg" | "lightgbm";

export interface PredictResponse {
  prediction_id: number;
  predicted_price: number;
  model: string;
  serving_mode: string;
  latency_ms: number;
}

export interface PredictionRecord {
  id: number;
  created_at: string;
  model: string;
  serving_mode: string;
  features: HouseFeatures;
  predicted_price: number;
  latency_ms: number;
}

export async function predict(
  features: HouseFeatures,
  model: ModelName,
): Promise<PredictResponse> {
  const resp = await fetch(`${BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ features, model }),
  });
  if (!resp.ok) throw new Error(`predict failed: ${resp.status}`);
  return resp.json();
}

export async function fetchHistory(limit = 20): Promise<PredictionRecord[]> {
  const resp = await fetch(`${BASE}/predictions?limit=${limit}`);
  if (!resp.ok) throw new Error(`history failed: ${resp.status}`);
  return resp.json();
}
