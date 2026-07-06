// Explainability panel: pick a model, see WHY it predicts what it does.
// linreg  -> coefficient bars (its whole story)
// lightgbm-> the split structure of one of its trees (feature-space partition)

import { useEffect, useState } from "react";
import type { LightgbmExplanation, LinregExplanation, ModelName } from "../../api";
import { fetchLightgbmExplanation, fetchLinregExplanation } from "../../api";
import CoefficientBars from "./CoefficientBars";
import TreePartition from "./TreePartition";

export default function ExplainPanel() {
  const [model, setModel] = useState<ModelName>("lightgbm");
  const [linreg, setLinreg] = useState<LinregExplanation | null>(null);
  const [lgbm, setLgbm] = useState<LightgbmExplanation | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    if (model === "linreg" && !linreg) {
      fetchLinregExplanation().then(setLinreg).catch((e) => setError(String(e)));
    }
    if (model === "lightgbm" && !lgbm) {
      fetchLightgbmExplanation().then(setLgbm).catch((e) => setError(String(e)));
    }
  }, [model, linreg, lgbm]);

  return (
    <section>
      <h2>
        Why does{" "}
        <select value={model} onChange={(e) => setModel(e.target.value as ModelName)}>
          <option value="lightgbm">lightgbm</option>
          <option value="linreg">linreg</option>
        </select>{" "}
        predict that?
      </h2>

      {error && <p className="error">{error}</p>}

      {model === "linreg" && linreg && (
        <>
          <p>
            Price = {Math.round(linreg.intercept).toLocaleString()} + each feature ×
            its coefficient. Green pushes the price up, red pulls it down.
          </p>
          <CoefficientBars coefficients={linreg.coefficients} />
        </>
      )}

      {model === "lightgbm" && lgbm && (
        <>
          <p>
            Tree {lgbm.tree_index + 1} of {lgbm.n_trees}: each split partitions the
            feature space; leaves hold that region's contribution (first 4 levels shown).
          </p>
          <TreePartition root={lgbm.tree} />
        </>
      )}
    </section>
  );
}
