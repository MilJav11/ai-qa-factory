import { test, expect } from '@playwright/test';

test('Test formulára kontaktný', async ({ page }) => {
  // Navigácia na stránku
  await page.goto('https://ubytovanie-stiavnica.sk/');

  // Kliknutie na odkazy v menu
  await page.locator('a', { hasText: 'ÚVOD' }).first().click();
  await page.locator('a', { hasText: 'GALÉRIA' }).first().click();
  await page.locator('a', { hasText: 'REZERVÁCIA' }).first().click();
  await page.locator('a', { hasText: 'KONTAKTY' }).first().click();

  // Vyplnenie formulára
  const menoInput = page.locator('#meno');
  const emailInput = page.locator('#email');
  const spravaInput = page.locator('#sprava');
  await menoInput.first().fill('Testovacie meno');
  await emailInput.first().fill('test@example.com');
  await spravaInput.first().fill('Testovacia sprava');

  // Odoslanie formulára
  const odoslatButton = page.locator('button', { hasText: 'Odoslať' });
  await odoslatButton.first().click();

  // Overenie úspešnosti odoslanie
  await expect(page.locator('div', { hasText: 'Správa bola úspešne odoslaná' })).toBeVisible();

  // Add a timeout to wait for the locator to be visible
  await page.waitForTimeout(5000);
  await page.locator('a', { hasText: 'KONTAKTY' }).first().waitFor({ timeout: 30000 });
  await page.locator('a', { hasText: 'KONTAKTY' }).first().click({ timeout: 30000 });
});