// Playwright e2e config. Expects the BACKEND already running on :8000 with
// trained models (make up + make seed + make train + make run-backend);
// Playwright starts the frontend dev server itself.
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:5173',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
  },
})
