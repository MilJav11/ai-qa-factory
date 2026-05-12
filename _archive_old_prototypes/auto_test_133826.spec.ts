import { test, expect } from '@playwright/test';

test('Kontakty', async ({ page }) => {
  // Odoberieme hlavičku stránky
  await page.goto('https://ubytovanie-stiavnica.sk/kontakty/');

  // Očakujeme, že bude viditeľný kontaktný formulár
  const formulár = page.locator('input[name="wpforms[fields][0]"]');
  await expect(formulár).toBeVisible();

  // Vložime falošné údaje do formulára
  await formulár.fill('Falošné meno');
  await page.locator('input[name="wpforms[fields][1]"]').fill('Falošná emailová adresa');
  await page.locator('textarea[name="wpforms[fields][2]"]').fill('Falošný text');

  // Mockujeme odoslanie formulára
  await page.route('**/*', route => route.fulfill({ status: 200, body: 'mocked' }));

  // Klikneme na tlačidlo "Odoslať"
  await page.locator('button[name="wpforms[submit]"]').click({ force: true });

  // Očakujeme, že bude viditeľná úspešná odpoveď
  const úspešnáOdpoveď = page.locator('text=Odoslané');
  await expect(úspešnáOdpoveď).toBeVisible();
});