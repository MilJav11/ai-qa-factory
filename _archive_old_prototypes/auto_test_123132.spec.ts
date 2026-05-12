import { test, expect } from '@playwright/test';

class AlzaPage {
  private page: any;

  constructor(page: any) {
    this.page = page;
  }

  get searchInput() {
    return this.page.locator('input[name="search"]').first();
  }

  get searchResults() {
    return this.page.locator('.item').first();
  }

  get addToCartButton() {
    return this.page.locator('button[data-gtag="buy-now"]').first();
  }

  async searchForProduct(productName: string) {
    await this.searchInput.fill(productName);
    await this.searchInput.press('Enter');
    await this.page.waitForLoadState('networkidle');
  }

  async openFirstProduct() {
    await this.searchResults.click();
    await this.page.waitForLoadState('networkidle');
  }

  async checkProductDetail() {
    await expect(this.addToCartButton).toBeVisible();
  }
}

test('Alza search test', async ({ page }) => {
  const alzaPage = new AlzaPage(page);
  await page.goto('https://www.alza.sk');
  await alzaPage.searchForProduct('iPhone 15');
  await alzaPage.openFirstProduct();
  await alzaPage.checkProductDetail();
});