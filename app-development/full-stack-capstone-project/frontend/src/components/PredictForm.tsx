// The prediction form: 12 feature inputs + model picker -> POST /predict.
// State is one flat `features` object mirroring the API contract, so
// submitting is just `predict(features, model)` with no reshaping.

import { useState } from "react";
import type { HouseFeatures, ModelName, PredictResponse } from "../api";
import { predict } from "../api";

const DEFAULTS: HouseFeatures = {
  area: 7420,
  bedrooms: 4,
  bathrooms: 2,
  stories: 3,
  mainroad: true,
  guestroom: false,
  basement: false,
  hotwaterheating: false,
  airconditioning: true,
  parking: 2,
  prefarea: true,
  furnishingstatus: "furnished",
};

// Field lists drive the rendering below — add a feature once, get an input.
const NUMBER_FIELDS = ["area", "bedrooms", "bathrooms", "stories", "parking"] as const;
const BOOL_FIELDS = [
  "mainroad",
  "guestroom",
  "basement",
  "hotwaterheating",
  "airconditioning",
  "prefarea",
] as const;

interface Props {
  onPredicted: () => void; // parent refreshes the history list
}

export default function PredictForm({ onPredicted }: Props) {
  const [features, setFeatures] = useState<HouseFeatures>(DEFAULTS);
  const [model, setModel] = useState<ModelName>("lightgbm");
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const set = (key: keyof HouseFeatures, value: number | boolean | string) =>
    setFeatures((f) => ({ ...f, [key]: value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const resp = await predict(features, model);
      setResult(resp);
      onPredicted(); // tell the parent so HistoryList refetches
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="predict-form">
      <h2>Predict a house price</h2>

      {NUMBER_FIELDS.map((name) => (
        <label key={name}>
          {name}
          <input
            type="number"
            value={features[name]}
            onChange={(e) => set(name, Number(e.target.value))}
          />
        </label>
      ))}

      {BOOL_FIELDS.map((name) => (
        <label key={name} className="checkbox">
          <input
            type="checkbox"
            checked={features[name]}
            onChange={(e) => set(name, e.target.checked)}
          />
          {name}
        </label>
      ))}

      <label>
        furnishing
        <select
          value={features.furnishingstatus}
          onChange={(e) => set("furnishingstatus", e.target.value)}
        >
          <option value="furnished">furnished</option>
          <option value="semi-furnished">semi-furnished</option>
          <option value="unfurnished">unfurnished</option>
        </select>
      </label>

      <label>
        model
        <select value={model} onChange={(e) => setModel(e.target.value as ModelName)}>
          <option value="lightgbm">lightgbm</option>
          <option value="linreg">linreg</option>
        </select>
      </label>

      <button type="submit" disabled={busy}>
        {busy ? "predicting…" : "Predict"}
      </button>

      {result && (
        <p className="result">
          Predicted price:{" "}
          <strong data-testid="predicted-price">
            {Math.round(result.predicted_price).toLocaleString()}
          </strong>{" "}
          <small>
            ({result.model}, {result.serving_mode}, {result.latency_ms.toFixed(1)} ms)
          </small>
        </p>
      )}
      {error && <p className="error">{error}</p>}
    </form>
  );
}
