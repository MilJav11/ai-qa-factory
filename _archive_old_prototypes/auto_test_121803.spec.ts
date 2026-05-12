// File: alza.sk.test.ts

import { test, expect } from '@playwright/test';

class AlzaPage {
  private page: any;

  constructor(page: any) {
    this.page = page;
  }

  get searchInput() {
    return this.page.locator('#search").first();
  }

  get searchResults() {
    return this.page.locator('.item').first();
  }

  get addToCartButton() {
    return this.page.locator('#buyButton").first();
  }

  async searchForProduct(productName: string) {
    await this.searchInput.fill(productName);
    await this.searchInput.press('Enter');
  }

  async openFirstSearchResult() {
    await this.searchResults.click();
  }

  async isProductDetailPage() {
    await expect(this.addToCartButton).toBeVisible();
  }
}

test('Alza.sk test', async ({ page }) => {
  const alzaPage = new AlzaPage(page);
  await page.goto('https://www.alza.sk');
  await alzaPage.searchForProduct('iPhone 15');
  await alzaPage.openFirstSearchResult();
  await alzaPage.isProductDetailPage();
});