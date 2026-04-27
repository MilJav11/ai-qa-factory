import { test as baseTest } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export const test = baseTest.extend({
  page: async ({ page }, use, testInfo) => {
    await use(page);

    // If test fails, save DOM dump
    if (testInfo.status !== 'passed' && testInfo.status !== 'skipped') {
      try {
        const dom = await page.content();
        const domPath = path.join(process.cwd(), 'dom_dump.txt');
        fs.writeFileSync(domPath, dom, 'utf-8');
        console.log(`🛡️ Guardian Fixture: DOM dump saved to ${domPath}`);
      } catch (e) {
        console.error('🛡️ Guardian Fixture: Failed to save DOM dump', e);
      }
    }
  },
});

export { expect } from '@playwright/test';
