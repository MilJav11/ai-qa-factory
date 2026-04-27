import { test, expect } from './fixtures';

test('Guardian Demo Test', async ({ page }) => {
    // Tento test je navrhnutý tak, aby zlyhal a aktivoval AI Guardiana
    await page.goto('https://example.com');

    // Tento element neexistuje, čo spôsobí timeout/failure
    await page.locator('#non-existent-button-id-for-ai-healing').click();
});