// End-to-end test — THE one test that crosses browser -> API -> model -> DB.
// Kept to a single happy path on purpose (e2e tests are slow and brittle;
// the pyramid says: many unit, some integration, FEW e2e).

import { expect, test } from '@playwright/test'

test('user predicts a price and sees it in the history list', async ({ page }) => {
  await page.goto('/')

  // The form is pre-filled with sensible defaults — just submit it.
  await page.getByRole('button', { name: /predict/i }).click()

  // A real model produced a price...
  const price = page.getByTestId('predicted-price')
  await expect(price).toBeVisible()
  const priceText = await price.textContent()
  expect(Number(priceText!.replace(/,/g, ''))).toBeGreaterThan(0)

  // ...and the prediction row landed in the history table (from Postgres).
  await expect(page.locator('table.history tbody tr').first()).toBeVisible()
})
