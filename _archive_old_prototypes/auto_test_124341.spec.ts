import { test, expect } from '@playwright/test';

test('Wikipedia search test', async ({ page }) => {
  // Navigate to Wikipedia
  await page.goto('https://sk.wikipedia.org/');

  // Find the search input field
  const searchInput = page.locator('#searchInput');

  // Enter the search term
  await searchInput.fill('Automatizácia');

  // Press Enter to submit the search
  await searchInput.press('Enter');

  // Wait for the page to load
  await page.waitForLoadState('networkidle');

  // Check if the main heading of the page is visible
  const heading = page.locator('#firstHeading');
  await expect(heading).toBeVisible();
});