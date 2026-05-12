import { test, expect } from '@playwright/test';

test('should test the website', async ({ page }) => {
  // Go to the website
  await page.goto('https://ubytovanie-stiavnica.sk/');

  // Click on the "Preskočiť na obsah" link with force
  await page.locator('text="Preskočiť na obsah"').first().click({ force: true });

  // Check if the "ÚVOD" link is visible
  await expect(page.locator('text="ÚVOD"').first()).toBeVisible();

  // Check if the "GALÉRIA" link is visible
  await expect(page.locator('text="GALÉRIA"').first()).toBeVisible();

  // Check if the "REZERVÁCIA" link is visible
  await expect(page.locator('text="REZERVÁCIA"').first()).toBeVisible();

  // Check if the "KONTAKTY" link is visible
  await expect(page.locator('text="KONTAKTY"').first()).toBeVisible();

  // Click on the "Pozrieť termíny a ceny" link with force
  await page.locator('text="Pozrieť termíny a ceny"').first().click({ force: true });

  // Check if the "TravelHacker" link is visible
  await expect(page.locator('text="TravelHacker"').first()).toBeVisible();

  // Check if the "banskastiavnica.travel" link is visible
  await expect(page.locator('text="banskastiavnica.travel"').first()).toBeVisible();

  // Check if the "travelhacker.blog" link is visible
  await expect(page.locator('text="travelhacker.blog"').first()).toBeVisible();

  // Check if the "slovakia.travel" link is visible
  await expect(page.locator('text="slovakia.travel"').first()).toBeVisible();

  // Click on the "Overiť voľné termíny" link with force
  await page.locator('text="Overiť voľné termíny"').first().click({ force: true });

  // Check if the "Facebook" link is visible
  await expect(page.locator('text="Facebook"').first()).toBeVisible();

  // Check if the "Instagram" link is visible
  await expect(page.locator('text="Instagram"').first()).toBeVisible();

  // Click on the "scroll-to-top" button
  await page.locator('#scroll-to-top').click();
});