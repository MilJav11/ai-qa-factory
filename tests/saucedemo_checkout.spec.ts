import { test, expect } from './fixtures';

test('complete SauceDemo checkout flow', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');

  await page.locator('[data-test="username"]').fill('standard_user');
  await page.locator('[data-test="password"]').fill('secret_sauce');
  await page.locator('[data-test="login-button"]').click();

  await expect(page.locator('.title')).toContainText('Products');

  await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
  await page.locator('.shopping_cart_link').click();

  await expect(page.locator('.inventory_item_name')).toContainText('Sauce Labs Backpack');

  await page.locator('[data-test="checkout"]').click();

  await page.locator('[data-test="firstName"]').fill('Milos');
  await page.locator('[data-test="lastName"]').fill('QA Expert');
  await page.locator('[data-test="postalCode"]').fill('12345');
  await page.locator('[data-test="continue"]').click();

  await page.locator('[data-test="finish"]').click();

  await expect(page.locator('.complete-header')).toContainText('Thank you for your order');
});