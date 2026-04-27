import { test as base, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Custom Playwright test object with "Test Guardian" logic.
 * Triggers on failure to dump a cleaned DOM for AI self-healing.
 */
export const test = base.extend<{}>({
  // No specific fixtures needed for this extension, but we use the test.afterEach hook below.
});

test.afterEach(async ({ page }, testInfo) => {
  // 1. Zisti, či test zlyhal (if (testInfo.status !== 'passed' && testInfo.status !== 'skipped'))
  if (testInfo.status !== 'passed' && testInfo.status !== 'skipped') {
    console.log(`[Guardian Hook] Test failed: "${testInfo.title}". Dumping cleaned DOM...`);

    try {
      // 2. Chirurgický filter priamo na stránke
      const cleanedDom = await page.evaluate(() => {
        // Vytvoríme klon body, aby sme nemanipulovali so živou stránkou (ak by to bolo treba pre trace)
        // Ale v Playwright po zlyhaní je to väčšinou jedno.
        const bodyClone = document.body.cloneNode(true) as HTMLElement;

        // Elementy na odstránenie: 'nav', 'footer', 'header', 'script', 'style', 'noscript', 'svg'
        const selectorsToRemove = ['nav', 'footer', 'header', 'script', 'style', 'noscript', 'svg'];
        
        selectorsToRemove.forEach(selector => {
          const elements = bodyClone.querySelectorAll(selector);
          elements.forEach(el => el.remove());
        });

        // Vráť iba vnútorné HTML (innerHTML) dôležitého obsahu
        return bodyClone.innerHTML;
      });

      // 3. Uloženie do dom_dump.txt v koreňovom adresári projektu
      const dumpPath = path.join(process.cwd(), 'dom_dump.txt');
      fs.writeFileSync(dumpPath, cleanedDom, 'utf-8');
      
      console.log(`[Guardian Hook] Cleaned DOM successfully saved to: ${dumpPath}`);
    } catch (error) {
      console.error(`[Guardian Hook] Error during DOM dump:`, error);
    }
  }
});

export { expect } from '@playwright/test';
