import { test, expect } from '@playwright/test';

test('should find search input, type "Automatizácia" and confirm it', async ({ page }) => {
  // Navigate to the page
  await page.goto('https://sk.wikipedia.org/');

  // Find the search input
  const searchInput = page.locator('#searchInput').first();

  // Type "Automatizácia" into the search input
  await searchInput.fill('Automatizácia');

  // Confirm the search
  await searchInput.press('Enter');

  // Wait for the results to load
  await page.waitForLoadState('networkidle');

  // Check if any results are visible
  const results = page.locator('.mw-search-result').first();
  await expect(results).toBeVisible();
});