import { defineConfig, devices } from "@playwright/test";

/**
 * E2E smoke for FleetPilot web.
 * Requires:
 *   - API on http://localhost:8800 (.\scripts\start-local.ps1)
 *   - Web on http://localhost:3000 (npm run dev)
 *
 * Skip automatically if API health fails:
 *   $env:PLAYWRIGHT_SKIP_API="1"; npm run test:e2e
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
