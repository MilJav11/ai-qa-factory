import { test, expect } from '@playwright/test';

class AlzaPage {
  private page: any;

  constructor(page: any) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('https://www.alza.sk');
  }

  async searchForProduct(productName: string) {
    const searchInput = this.page.locator('#searchbox').first();
    await searchInput.fill(productName);
    await searchInput.press('Enter');
  }

  async clickOnFirstProduct() {
    const productLink = this.page.locator('.product').first();
    await productLink.click();
  }

  async checkAddToCartButton() {
    const addToCartButton = this.page.locator('text="Pridať do košíka"').first();
    await expect(addToCartButton).toBeVisible();
  }
}

test('Alza search test', async ({ page }) => {
  const alzaPage = new AlzaPage(page);
  await alzaPage.goto();
  await alzaPage.searchForProduct('iPhone 15');
  await alzaPage.clickOnFirstProduct();
  await alzaPage.checkAddToCartButton();
});