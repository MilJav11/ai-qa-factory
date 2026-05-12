import { test, expect } from "@playwright/test";

test("should login successfully", async ({ page }) => {
  await page.goto("https://www.saucedemo.com/");

  await page.route('**/*', r => r.fulfill({ status: 200, body: 'ok' }));

  await page.fill("#user-name", "standard_user");
  await page.fill("#password", "secret_sauce");

  await page.click("#login-button", { force: true });

  await expect(page.locator("#header_container")).toContainText("Products");
});