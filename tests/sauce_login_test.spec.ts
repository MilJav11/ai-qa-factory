import { test, expect } from './fixtures';

test('Successful login and products page verification', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');

  await page.locator('input[data-test="username"]').fill('standard_user');
  await page.locator('input[data-test="password"]').fill('secret_sauce');
  await page.locator('input[data-test="login-button"]').click();

  await expect(page.locator('span.title')).toHaveText('Products');
});