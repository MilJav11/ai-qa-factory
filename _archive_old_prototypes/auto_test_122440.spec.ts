// File: alzaTest.ts
import { test, expect } from '@playwright/test';

class AlzaPage {
  private page: any;

  constructor(page: any) {
    this.page = page;
  }

  get searchInput() {
    return this.page.locator('input[name="search"]').first();
  }

  get searchResult() {
    return this.page.locator('.item').first();
  }

  get addToCartButton() {
    return this.page.locator('button:has-text("Pridať do košíka")').first();
  }

  async searchForProduct(productName: string) {
    await this.searchInput.fill(productName);
    await this.searchInput.press('Enter');
    await this.page.waitForLoadState('networkidle');
  }

  async openFirstSearchResult() {
    await this.searchResult.click();
    await this.page.waitForLoadState('networkidle');
  }

  async checkIfProductDetailIsOpen() {
    await expect(this.addToCartButton).toBeVisible();
  }
}

test('Alza test', async ({ page }) => {
  const alzaPage = new AlzaPage(page);
  await page.goto('https://www.alza.sk');
  await alzaPage.searchForProduct('iPhone 15');
  await alzaPage.openFirstSearchResult();
  await alzaPage.checkIfProductDetailIsOpen();
});