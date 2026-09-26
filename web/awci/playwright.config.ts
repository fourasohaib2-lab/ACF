import { existsSync } from "node:fs";
import { defineConfig } from "@playwright/test";

// The container ships a Chromium build that may differ from the one this @playwright/test expects.
const chromium = process.env.AWCI_CHROMIUM ?? "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

export default defineConfig({
  testDir: "e2e",
  timeout: 60_000,
  workers: 1,
  reporter: [["list"]],
  expect: { toHaveScreenshot: { maxDiffPixelRatio: 0.02 } },
  use: {
    baseURL: "http://127.0.0.1:8099",
    viewport: { width: 1440, height: 900 },
    launchOptions: {
      executablePath: existsSync(chromium) ? chromium : undefined,
      args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"],
    },
  },
  webServer: {
    // Real cropped IFS fixtures, offline EUMETView relay (tools/awci/e2e_server.py), built front.
    command: "npm run build && ../../.venv/bin/python ../../tools/awci/e2e_server.py --port 8099",
    url: "http://127.0.0.1:8099/api/v1/awci/domains",
    reuseExistingServer: !process.env.CI,
    timeout: 240_000,
  },
});
