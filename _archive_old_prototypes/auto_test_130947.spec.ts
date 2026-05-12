import { test, expect } from '@playwright/test';

test('Nájdi', async ({ page }) => {
  await page.goto('https://ubytovanie-stiavnica.sk/');

  // Preskočiť na obsah
  const skipToContentLink = page.locator('a', { hasText: 'Preskočiť na obsah' });
  await skipToContentLink.first().waitFor({ state: 'visible' });
  await skipToContentLink.first().click({ timeout: 60000 });

  // ÚVOD
  const uvodLink = page.locator('a', { hasText: 'ÚVOD' });
  await uvodLink.first().waitFor({ state: 'visible' });
  await uvodLink.first().click({ timeout: 60000 });

  // GALÉRIA
  const galeriaLink = page.locator('a', { hasText: 'GALÉRIA' });
  await galeriaLink.first().waitFor({ state: 'visible' });
  await galeriaLink.first().click({ timeout: 60000 });

  // REZERVÁCIA
  const rezervaciaLink = page.locator('a', { hasText: 'REZERVÁCIA' });
  await rezervaciaLink.first().waitFor({ state: 'visible' });
  await rezervaciaLink.first().click({ timeout: 60000 });

  // KONTAKTY
  const kontaktyLink = page.locator('a', { hasText: 'KONTAKTY' });
  await kontaktyLink.first().waitFor({ state: 'visible' });
  await kontaktyLink.first().click({ timeout: 60000 });

  // Menu navigácie
  const menuNavigacieButton = page.locator('button', { hasText: 'Menu navigácie' });
  await menuNavigacieButton.first().waitFor({ state: 'visible' });
  await menuNavigacieButton.first().click({ timeout: 60000 });

  // Pozrieť termíny a ceny
  const pozrietTerminyACenyLink = page.locator('a', { hasText: 'Pozrieť termíny a ceny' });
  await pozrietTerminyACenyLink.first().waitFor({ state: 'visible' });
  await pozrietTerminyACenyLink.first().click({ timeout: 60000 });

  // Overiť voľné termíny
  const overitVolneTerminyLink = page.locator('a', { hasText: 'Overiť voľné termíny' });
  await overitVolneTerminyLink.first().waitFor({ state: 'visible' });
  await overitVolneTerminyLink.first().click({ timeout: 60000 });

  // Facebook
  const facebookLink = page.locator('a', { hasText: 'Facebook' });
  await facebookLink.first().waitFor({ state: 'visible' });
  await facebookLink.first().click({ timeout: 60000 });

  // Instagram
  const instagramLink = page.locator('a', { hasText: 'Instagram' });
  await instagramLink.first().waitFor({ state: 'visible' });
  await instagramLink.first().click({ timeout: 60000 });

  // Scroll to top
  const scrollToTopButton = page.locator('button#scroll-to-top');
  await scrollToTopButton.first().waitFor({ state: 'visible' });
  await scrollToTopButton.first().click({ timeout: 60000 });

  // Verify page title
  await expect(page).toHaveTitle('Ubytovanie Štiavnica');

  // Verify page content
  await expect(page.locator('h1')).toContainText('Ubytovanie Štiavnica');
});