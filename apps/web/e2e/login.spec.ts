import { expect, test } from "@playwright/test";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8800";

test.beforeAll(async ({ request }) => {
  if (process.env.PLAYWRIGHT_SKIP_API === "1") {
    test.skip(true, "PLAYWRIGHT_SKIP_API=1");
  }
  try {
    const res = await request.get(`${API}/api/v1/health`);
    if (!res.ok()) {
      test.skip(true, `API health not ok at ${API}`);
    }
  } catch {
    test.skip(true, `API unreachable at ${API} — run .\\scripts\\start-local.ps1`);
  }
});

test("login → dashboard", async ({ page }) => {
  await page.goto("/login/");

  await expect(page.getByTestId("login-page")).toBeVisible();

  // Wait until API status is not "checking"
  await expect(page.getByTestId("login-api-status")).not.toHaveText("Проверка API…", {
    timeout: 15_000,
  });

  const status = await page.getByTestId("login-api-status").textContent();
  if (status?.includes("недоступен")) {
    test.skip(true, "UI reports API down");
  }

  await page.getByTestId("login-email").fill("demo@fleetpilot.ru");
  await page.getByTestId("login-password").fill("Demo12345!");
  await page.getByTestId("login-submit").click();

  await expect(page.getByTestId("app-shell")).toBeVisible({ timeout: 20_000 });
  await expect(page.getByTestId("page-title")).toContainText(/Экономия|ROI/i);
  await expect(page.getByTestId("dashboard-kpi")).toBeVisible();
});
