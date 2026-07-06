/// <reference types="vitest/config" />
// Vite build config + Vitest settings in one file (Vitest reads `test`).
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',        // simulate a browser DOM for component tests
    globals: true,               // describe/it/expect without imports
    setupFiles: './tests/setup.ts',
    include: ['tests/unit/**/*.test.tsx'],
  },
})
