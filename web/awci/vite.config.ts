/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The API (acf-awci-web, port 8091) serves the built front on "/" in production (same origin);
// in development Vite proxies /api to it.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8091" } },
  build: { sourcemap: true, chunkSizeWarningLimit: 1200 },
  // MapLibre's module worker imports a shared chunk: bundle it as an ES worker (see MapView setWorkerUrl).
  worker: { format: "es" },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
