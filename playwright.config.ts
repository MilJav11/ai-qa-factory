import { defineConfig } from '@playwright/test';
import * as dotenv from 'dotenv';

// This unlocks the .env file for all future tests
dotenv.config();

export default defineConfig({
  testDir: './tests',
  reporter: [
    ['list'],
    ['./guardian_reporter.ts']
  ],
  use: {
    // Thanks to this, you don't even need to write --headed in the terminal anymore
    headless: false, 
    viewport: { width: 1280, height: 720 },
    trace: 'retain-on-failure',
  },
});
