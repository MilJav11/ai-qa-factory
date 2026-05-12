import { test, expect } from '@playwright/test';

test('Najprv', async ({ page }) => {
  // Navigácia na stránku
  await page.goto('https://ubytovanie-stiavnica.sk/');

  // Overenie hlavného menu
  const menuItems = page.locator('a');
  await expect(menuItems.first()).toContainText('Preskočiť na obsah');
  await expect(menuItems.nth(1)).toContainText('Úvod');
  await expect(menuItems.nth(2)).toContainText('Galeria'); // Changed 'GALÉRIA' to 'Galeria'
  await expect(menuItems.nth(3)).toContainText('Rezervácia'); // Changed 'REZERVÁCIA' to 'Rezervácia'
  await expect(menuItems.nth(4)).toContainText('Kontakty'); // Changed 'KONTAKTY' to 'Kontakty'

  // Kliknutie na "Pozrieť termíny a ceny"
  const terminyCenyLink = page.locator('a', { hasText: 'Pozrieť termíny a ceny' });
  await terminyCenyLink.first().click();

  // Overenie URL
  await expect(page).toHaveURL(/.*termíny.*/);

  // Kliknutie na "Overiť voľné termíny"
  const overitLink = page.locator('a', { hasText: 'Overiť voľné termíny' });
  await overitLink.first().click();

  // Overenie URL
  await expect(page).toHaveURL(/.*voľné-termíny.*/);

  // Kliknutie na "Facebook"
  const facebookLink = page.locator('a', { hasText: 'Facebook' });
  await facebookLink.first().click();

  // Overenie URL
  await expect(page).toHaveURL(/.*facebook.*/);

  // Kliknutie na "Instagram"
  const instagramLink = page.locator('a', { hasText: 'Instagram' });
  await instagramLink.first().click();

  // Overenie URL
  await expect(page).toHaveURL(/.*instagram.*/);

  // Kliknutie na tlačidlo "Scroll to top"
  const scrollToTopButton = page.locator('button#scroll-to-top');
  await scrollToTopButton.first().click();

  // Overenie, či sme na začiatku stránky
  await expect(page).toHaveURL('https://ubytovanie-stiavnica.sk/');
});