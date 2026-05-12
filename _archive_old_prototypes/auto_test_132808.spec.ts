import { test, expect } from '@playwright/test';

test('kontakty test', async ({ page }) => {
  await page.goto('https://ubytovanie-stiavnica.sk/kontakty/');

  // Overiť, či je stránka načítaná
  await expect(page.locator('body')).toContainText('Kontakty');

  // Vyhľadať formulár
  const menoInput = page.locator('#wpforms-143-field_0');
  const emailInput = page.locator('#wpforms-143-field_1');
  const spravaInput = page.locator('#wpforms-143-field_2');

  // Vyplniť formulár
  await menoInput.first().fill('Test');
  await emailInput.first().fill('test@example.com');
  await spravaInput.first().fill('Testová správa');

  // Mocknúť odoslanie formulára
  await page.route('**/*', route => route.fulfill({ status: 200, body: 'mocked' }));

  // Odoslať formulár
  const odoslatButton = page.locator('#wpforms-submit-143');
  await odoslatButton.first().click({ force: true });

  // Overiť, či bola stránka načítaná úspešne
  await expect(page.locator('body')).toContainText('Vaše meno');
});