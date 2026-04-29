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
        const queueDir = path.join(process.cwd(), 'guardian_queue');
        if (!fs.existsSync(queueDir)) {
          fs.mkdirSync(queueDir, { recursive: true });
        }
        const safeTitle = testInfo.title.replace(/[^a-zA-Z0-9]/g, '_');
        const domPath = path.join(queueDir, `dom_dump_${safeTitle}.txt`);
        fs.writeFileSync(domPath, dom, 'utf-8');
        console.log(`🛡️ Guardian Fixture: DOM dump saved to ${domPath}`);
      } catch (e) {
        console.error('🛡️ Guardian Fixture: Failed to save DOM dump', e);
      }
    }
  },
});

export { expect } from '@playwright/test';
