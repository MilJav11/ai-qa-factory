import { defineConfig } from '@playwright/test';
import * as dotenv from 'dotenv';

// Toto odomkne .env súbor pre všetky budúce testy
dotenv.config();

export default defineConfig({
  reporter: [
    ['list'],
    ['./guardian_reporter.ts']
  ],
  use: {
    // Vďaka tomuto už ani nemusíš písať --headed do terminálu
    headless: false, 
    viewport: { width: 1280, height: 720 },
    trace: 'retain-on-failure',
  },
});
