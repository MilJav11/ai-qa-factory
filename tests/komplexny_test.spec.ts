import { test, expect } from './fixtures';

test('Login with valid credentials', async ({ page }) => {
  await page.goto('https://the-internet.herokuapp.com/login');

  await page.locator('input[name="username"]').fill('tomsmith');
  await page.locator('input[name="password"]').fill('SuperSecretPassword!');
  await page.locator('form#login button[type="submit"]').click();

  await expect(page.locator('#flash')).toContainText('secure');
});