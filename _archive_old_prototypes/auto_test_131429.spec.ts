import { test, expect } from '@playwright/test';

test('Kontaktný formulár', async ({ page }) => {
  // Navigácia na stránku
  await page.goto('https://ubytovanie-stiavnica.sk/');

  // Vyplnenie kontaktného formulára
  const menoInput = page.locator('#meno').first();
  const emailInput = page.locator('#email').first();
  const telefonInput = page.locator('#telefon').first();
  const spravaInput = page.locator('#sprava').first();

  // Wait for the input fields to be visible before filling them
  await expect(menoInput).toBeVisible({ timeout: 30000 });
  await expect(emailInput).toBeVisible({ timeout: 30000 });
  await expect(telefonInput).toBeVisible({ timeout: 30000 });
  await expect(spravaInput).toBeVisible({ timeout: 30000 });

  await menoInput.fill('Testovacie meno');
  await emailInput.fill('test@example.com');
  await telefonInput.fill('+421 123 456 789');
  await spravaInput.fill('Testovacia sprava');

  // Mockovanie odoslanie formulára
  await page.route('**/*', route => route.fulfill({ status: 200, body: 'mocked' }));

  // Odoslanie formulára
  const odoslatButton = page.locator('text="Odoslať"').first();
  await expect(odoslatButton).toBeVisible({ timeout: 30000 });
  await odoslatButton.click({ force: true });

  // Overenie úspešnosti odoslanie
  await page.waitForTimeout(1000);
  const podakovanie = page.locator('text="Ďakujeme za Vašu správu."').first();
  await expect(podakovanie).toBeVisible({ timeout: 30000 });
});