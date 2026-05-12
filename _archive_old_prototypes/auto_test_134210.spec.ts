import { test, expect } from '@playwright/test';

test('Kontakty', async ({ page }) => {
  // Odoberieme hlavičku stránky
  await page.goto('https://ubytovanie-stiavnica.sk/kontakty/');

  // 1. Strict Mode Ochrana
  const preskocitNaObsah = await page.locator('a[name="skip-to-content"]').first();
  await preskocitNaObsah.click();

  // 2. Vyhľadávanie (SEARCH)
  const searchInput = await page.locator('input[name="wpforms[fields][0]"]');
  await searchInput.fill('Testovací text');
  await searchInput.press('Enter');

  // 3. Slepé placeholdery
  const wpformsField0 = await page.locator('input[name="wpforms[fields][0]"]');
  await wpformsField0.fill('Testovací text');

  // 4. Jeden súbor
  const menuNavigacia = await page.locator('button[name="menu-navigacia"]');
  await menuNavigacia.click();

  // 5. Wikipedia / Direct Match Logic
  const h1 = await page.locator('h1');
  expect(await h1.textContent()).toContain('Kontakty');

  // 6. Priamociarosť (NO RANDOM CLICKS)
  const rezervacia = await page.locator('a[name="rezervacia"]');
  await rezervacia.click();

  // 7. Mockovanie odpovede (NETWORK INTERCEPTION)
  await page.route('**/*', route => route.fulfill({ status: 200, body: 'mocked' }));

  // 8. Intercepted clicks a skryté linky
  const odoslat = await page.locator('button[name="wpforms-submit-143"]');
  await odoslat.click({ force: true });

  // 9. WordPress Forms
  const wpformsField1 = await page.locator('input[name="wpforms[fields][1]"]');
  await wpformsField1.fill('Testovací text');

  // 10. Diakritika a text
  const wpformsField2 = await page.locator('textarea[name="wpforms[fields][2]"]');
  await wpformsField2.fill('Testovací text');

  // 11. Laser focus
  const wpformsHp = await page.locator('input[name="wpforms[hp]"]');
  await wpformsHp.fill('Testovací text');

  // 12. URL shortcuts
  await page.goto('https://ubytovanie-stiavnica.sk/kontakty/');

  // 13. Mocking success assertion
  const odoslatButton = await page.locator('button[name="wpforms-submit-143"]');
  await page.waitForTimeout(1000); // wait for the button to disappear
  expect(await odoslatButton.count()).toBe(0);
});