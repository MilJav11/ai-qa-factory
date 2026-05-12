import { test, expect } from "@playwright/test";

test("Vyplň kontaktný formulár a odoslať", async ({ page }) => {
  await page.goto("https://ubytovanie-stiavnica.sk/kontakty/");

  await page.route('**/*', route => route.fulfill({ status: 200, body: 'ok' }));

  await page.fill('#wpforms-143-field_0', 'Testové meno');
  await page.fill('#wpforms-143-field_1', 'test@example.com');
  await page.fill('#wpforms-143-field_2', 'Testová správa');

  await page.click('#wpforms-submit-143', { force: true });
});