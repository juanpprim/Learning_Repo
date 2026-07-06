// Root layout: form on the left, history on the right.
// `refreshKey` is the one piece of shared state — bumping it after a
// prediction tells HistoryList to refetch.

import { useState } from "react";
import "./App.css";
import HistoryList from "./components/HistoryList";
import PredictForm from "./components/PredictForm";

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <main className="layout">
      <header>
        <h1>Real-Time ML Platform</h1>
        <p>House-price prediction — LightGBM vs Linear Regression</p>
      </header>
      <div className="columns">
        <PredictForm onPredicted={() => setRefreshKey((k) => k + 1)} />
        <section>
          <h2>Recent predictions</h2>
          <HistoryList refreshKey={refreshKey} />
        </section>
      </div>
    </main>
  );
}
