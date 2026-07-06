// D3 view tests — learning goal: even viz is testable. Feed fixed fixture
// data, assert the right number of SVG elements render. No snapshotting of
// pixel positions (brittle); just the structural contract.

import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import CoefficientBars from "../../src/components/explain/CoefficientBars";
import TreePartition from "../../src/components/explain/TreePartition";
import type { TreeNode } from "../../src/api";

test("CoefficientBars renders one bar per coefficient", () => {
  const coefficients = [
    { feature: "area", coefficient: 350 },
    { feature: "bathrooms", coefficient: 400000 },
    { feature: "furnishingstatus_unfurnished", coefficient: -120000 },
  ];
  render(<CoefficientBars coefficients={coefficients} />);

  expect(screen.getAllByTestId("coef-bar")).toHaveLength(3);
  // Labels are visible text, not just tooltips.
  expect(screen.getByText("area")).toBeInTheDocument();
});

test("TreePartition renders every split and leaf as a node", () => {
  // A 3-level fixture: 2 splits + 3 leaves = 5 nodes.
  const tree: TreeNode = {
    feature: "area",
    threshold: 9000,
    left: {
      feature: "bathrooms",
      threshold: 2,
      left: { value: 100000 },
      right: { value: 250000 },
    },
    right: { value: 500000 },
  };
  render(<TreePartition root={tree} />);

  expect(screen.getAllByTestId("tree-node")).toHaveLength(5);
  expect(screen.getByText("area ≤ 9000")).toBeInTheDocument();
  expect(screen.getByText("500,000")).toBeInTheDocument();
});

test("TreePartition prunes below maxDepth", () => {
  // A deep chain: with maxDepth=1 only root + 2 children render.
  const deep: TreeNode = {
    feature: "a",
    threshold: 1,
    left: {
      feature: "b",
      threshold: 2,
      left: { value: 1 },
      right: { value: 2 },
    },
    right: { value: 3 },
  };
  render(<TreePartition root={deep} maxDepth={1} />);

  expect(screen.getAllByTestId("tree-node")).toHaveLength(3);
  expect(screen.getByText("…")).toBeInTheDocument(); // the collapsed subtree
});
