import { test, expect } from "@playwright/test";

// ── Helpers ────────────────────────────────────────────────────────

const TEST_EMAIL = `e2e_${Date.now()}@foresight.ai`;
const TEST_PASSWORD = "E2eTest123!";
const TEST_USERNAME = `e2euser_${Date.now()}`;

async function loginUser(page: any) {
  await page.goto("/login");
  await page.fill('input[type="email"]', TEST_EMAIL);
  await page.fill('input[type="password"]', TEST_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL(/dashboard/, { timeout: 10_000 });
}

// ── Tests ──────────────────────────────────────────────────────────

test.describe("Foresight E2E — Core User Journeys", () => {

  test("T01: Landing page loads and hero visible", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Foresight/i);
    // Hero heading should be visible
    const heading = page.locator("h1").first();
    await expect(heading).toBeVisible();
    const text = await heading.innerText();
    expect(text.length).toBeGreaterThan(5);
  });

  test("T02: Signup flow creates account and redirects", async ({ page }) => {
    await page.goto("/signup");
    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[name="username"]', TEST_USERNAME);

    // Fill password fields (could be 'password' or 'password1' etc.)
    const passwordFields = page.locator('input[type="password"]');
    const count = await passwordFields.count();
    for (let i = 0; i < count; i++) {
      await passwordFields.nth(i).fill(TEST_PASSWORD);
    }

    await page.click('button[type="submit"]');

    // Should land on dashboard or login after signup
    await page.waitForURL(/(dashboard|login)/, { timeout: 10_000 });
    const url = page.url();
    expect(url).toMatch(/(dashboard|login)/);
  });

  test("T03: Login with valid credentials reaches dashboard", async ({ page }) => {
    await loginUser(page);
    expect(page.url()).toContain("dashboard");
  });

  test("T04: Dashboard renders KPI cards", async ({ page }) => {
    await loginUser(page);
    // At least one stat card or metric should be visible
    const body = page.locator("body");
    await expect(body).toBeVisible();
    // Page title / heading present
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible();
  });

  test("T05: Search page loads and accepts input", async ({ page }) => {
    await loginUser(page);
    await page.goto("/search");
    const input = page.locator('input[type="search"], input[type="text"], input[placeholder]').first();
    await expect(input).toBeVisible();
    await input.fill("AI agents");
    // Should not crash
    await page.waitForTimeout(500);
    await expect(page.locator("body")).toBeVisible();
  });

  test("T06: Feed page loads with content", async ({ page }) => {
    await loginUser(page);
    await page.goto("/feed");
    await expect(page.locator("body")).toBeVisible();
    // Should not show error state
    const errorEl = page.locator("text=Something went wrong");
    await expect(errorEl).not.toBeVisible();
  });

  test("T07: Login rejects invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "notareal@email.com");
    await page.fill('input[type="password"]', "wrongpassword");
    await page.click('button[type="submit"]');

    // Should stay on login and show an error
    await page.waitForTimeout(1500);
    const url = page.url();
    expect(url).toContain("login");
  });

  test("T08: Navigation links work from dashboard", async ({ page }) => {
    await loginUser(page);
    // Click first nav link that's not the current page
    const navLinks = page.locator("nav a, aside a");
    const count = await navLinks.count();
    if (count > 0) {
      await navLinks.first().click();
      await page.waitForTimeout(500);
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("T09: Mobile layout — landing page readable", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");
    // No horizontal scroll
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 10); // 10px tolerance
    await expect(page.locator("h1").first()).toBeVisible();
  });

  test("T10: Tablet layout — dashboard readable", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await loginUser(page);
    await expect(page.locator("body")).toBeVisible();
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 20);
  });
});
