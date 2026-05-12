import { test, expect } from "@playwright/test";

test("SCENÁR: Otestuj validáciu povinných polí (Negative path)", async ({ page }) => {
  await page.goto("https://ubytovanie-stiavnica.sk/kontakty/");

  // Mockuj formulár
  await page.route('**/*', r => r.fulfill({status:200, body:'ok'}));

  // Klikni na submit bez vyplnenia povinných polí
  const submitButton = page.locator('text="Odoslať"');
  await submitButton.click({ force: true });

  // Over validáciu povinných polí
  const nameField = page.locator('#wpforms-143-field_0');
  const emailField = page.locator('#wpforms-143-field_1');
  const messageField = page.locator('#wpforms-143-field_2');

  // Použi iný locator pre nameField, pretože prvý bol chybný
  const nameField2 = page.locator('[name="wpforms[fields][0]"]');
  await expect(nameField2).toContainText('Pole je povinné', { insensitive: true });
  await expect(emailField).toContainText('Pole je povinné', { insensitive: true });
  await expect(messageField).toContainText('Pole je povinné', { insensitive: true });
});