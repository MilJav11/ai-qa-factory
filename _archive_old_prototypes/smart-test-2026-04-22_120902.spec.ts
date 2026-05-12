const { test, expect } = require('@playwright/test');

class WikipediaPage {
  page: any;

  constructor(page: any) {
    this.page = page;
  }

  get searchInput() {
    return this.page.locator('#searchInput');
  }

  get searchButton() {
    return this.page.locator('text="Hľadať"');
  }

  async searchFor(term: string) {
    await this.searchInput.fill(term);
    await this.searchInput.press('Enter');
  }
}

test('Wikipedia search test', async ({ page }) => {
  const wikipediaPage = new WikipediaPage(page);
  await page.goto('https://sk.wikipedia.org/');
  await wikipediaPage.searchFor('Umelá inteligencia');
  await expect(page.locator('body')).toContainText('Umelá inteligencia');
});