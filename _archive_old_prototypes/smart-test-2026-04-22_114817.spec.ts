// pages/LoginPage.ts
export class LoginPage {
  private page: any;

  constructor(page: any) {
    this.page = page;
  }

  get usernameInput() {
    return this.page.locator('#user-name');
  }

  get passwordInput() {
    return this.page.locator('#password');
  }

  get loginButton() {
    return this.page.locator('#login-button');
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}

// pages/InventoryPage.ts
export class InventoryPage {
  private page: any;

  constructor(page: any) {
    this.page = page;
  }

  get addToCartButton() {
    return this.page.locator('text="Add to cart"');
  }

  async addToCart() {
    await this.addToCartButton.first().click();
  }

  get cartIcon() {
    return this.page.locator('.shopping_cart_link');
  }

  async openCart() {
    await this.cartIcon.click();
  }
}

// pages/CartPage.ts
export class CartPage {
  private page: any;

  constructor(page: any) {
    this.page = page;
  }

  get cartHeader() {
    return this.page.locator('text="Your Cart"');
  }

  async isCartPage() {
    await this.cartHeader.waitFor();
  }
}

// tests/example.spec.ts
import { test, expect } from '@playwright/test';

test('should login and add to cart', async ({ page }) => {
  const loginPage = new LoginPage(page);
  const inventoryPage = new InventoryPage(page);
  const cartPage = new CartPage(page);

  await page.goto('https://www.saucedemo.com/');

  await loginPage.login('standard_user', 'secret_sauce');

  await inventoryPage.addToCart();
  await inventoryPage.openCart();

  await cartPage.isCartPage();

  await expect(cartPage.cartHeader).toBeVisible();
});