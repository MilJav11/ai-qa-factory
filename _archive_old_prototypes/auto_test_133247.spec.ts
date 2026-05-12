import { test, expect } from '@playwright/test';

test('kontakty test', async ({ page }) => {
  await page.goto('https://ubytovanie-stiavnica.sk/kontakty/');

  // Overenie názvu stránky
  await expect(page.locator('h1')).toContainText(/Kontakty/i);

  // Vyhľadanie formulára
  const menoInput = page.locator('#wpforms-143-field_0');
  const emailInput = page.locator('#wpforms-143-field_1');
  const spravaInput = page.locator('#wpforms-143-field_2');

  // Vyplnenie formulára
  await menoInput.fill('Testové meno');
  await emailInput.fill('test@example.com');
  await spravaInput.fill('Testová správa');

  // Mockovanie odoslanie formulára
  await page.route('**/*', route => route.fulfill({ status: 200, body: 'mocked' }));

  // Odoslanie formulára
  const odoslatButton = page.locator('#wpforms-submit-143');
  await odoslatButton.click({ force: true });

  // Overenie úspešného odoslanie
  await expect(page.locator('text="Odoslané"')).toBeVisible();
});