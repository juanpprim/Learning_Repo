// Component unit test — learning goal: test BEHAVIOR, not implementation.
// We don't inspect state or spy on internals; we do what a user does
// (click submit) and assert on what a user sees (the price appears).

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, test, vi } from "vitest";
import PredictForm from "../../src/components/PredictForm";

afterEach(() => vi.restoreAllMocks());

test("submitting the form shows the predicted price", async () => {
  // Mock fetch at the network boundary — the ONLY thing we fake.
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        prediction_id: 1,
        predicted_price: 4200000,
        model: "lightgbm",
        serving_mode: "direct",
        latency_ms: 12.3,
      }),
    }),
  );

  const onPredicted = vi.fn();
  render(<PredictForm onPredicted={onPredicted} />);

  await userEvent.click(screen.getByRole("button", { name: /predict/i }));

  // The user sees the formatted price...
  expect(await screen.findByTestId("predicted-price")).toHaveTextContent("4,200,000");
  // ...and the parent was told to refresh the history list.
  expect(onPredicted).toHaveBeenCalledOnce();
});

test("a failed request shows an error instead of a price", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));

  render(<PredictForm onPredicted={vi.fn()} />);
  await userEvent.click(screen.getByRole("button", { name: /predict/i }));

  expect(await screen.findByText(/predict failed: 500/)).toBeInTheDocument();
  expect(screen.queryByTestId("predicted-price")).not.toBeInTheDocument();
});
