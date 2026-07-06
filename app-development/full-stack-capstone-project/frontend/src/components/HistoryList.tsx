// Recent predictions table. The parent bumps `refreshKey` after each submit,
// which re-triggers the effect — simplest possible "refetch" signal.

import { useEffect, useState } from "react";
import type { PredictionRecord } from "../api";
import { fetchHistory } from "../api";

interface Props {
  refreshKey: number;
}

export default function HistoryList({ refreshKey }: Props) {
  const [rows, setRows] = useState<PredictionRecord[]>([]);

  useEffect(() => {
    fetchHistory().then(setRows).catch(console.error);
  }, [refreshKey]);

  if (rows.length === 0) return <p>No predictions yet.</p>;

  return (
    <table className="history">
      <thead>
        <tr>
          <th>#</th>
          <th>price</th>
          <th>model</th>
          <th>mode</th>
          <th>latency</th>
          <th>area</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id}>
            <td>{r.id}</td>
            <td>{Math.round(r.predicted_price).toLocaleString()}</td>
            <td>{r.model}</td>
            <td>{r.serving_mode}</td>
            <td>{r.latency_ms.toFixed(1)} ms</td>
            <td>{r.features.area}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
