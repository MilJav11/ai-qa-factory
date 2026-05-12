// wikipedia.page.ts
import { Page } from '@playwright/test';

export class WikipediaPage {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  get searchInput() {
    return this.page.locator('#searchInput');
  }

  get searchButton() {
    return this.page.locator('button', { hasText: 'Hľadať' });
  }

  async searchForTerm(term: string) {
    await this.searchInput.fill(term);
    await this.searchButton.click();
  }

  async waitForSearchResults() {
    await this.page.waitForLoadState('networkidle');
  }

  async verifySearchResult(term: string) {
    const url = this.page.url();
    expect(url).toContain(`wiki/${term}`);
  }
}

// wikipedia.test.ts
import { test, expect } from '@playwright/test';
import { WikipediaPage } from './wikipedia.page';

test('should search for term and verify result', async ({ page }) => {
  const wikipediaPage = new WikipediaPage(page);
  await page.goto('https://sk.wikipedia.org/');
  await wikipediaPage.searchForTerm('Umelá inteligencia');
  await wikipediaPage.waitForSearchResults();
  await wikipediaPage.verifySearchResult('Umelá_inteligencia');
});