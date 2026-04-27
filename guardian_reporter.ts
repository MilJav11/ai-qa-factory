import { Reporter, TestCase, TestResult } from '@playwright/test/reporter';
import * as fs from 'fs';
import * as path from 'path';

class GuardianReporter implements Reporter {
  onTestEnd(test: TestCase, result: TestResult) {
    if (result.status === 'failed' || result.status === 'timedOut') {
      // 🚨 CHANGE: Traverse all error details captured by Playwright
      let fullError = result.errors.map(err => err.stack || err.message).join('\n\n');
      
      // If errors array is empty, try at least basic error
      if (!fullError && result.error) {
        fullError = result.error.stack || result.error.message || 'No error message';
      }

      // Clean ANSI escape codes (colors)
      fullError = fullError.replace(/\x1b\[[0-9;]*m/g, '');

      const logPath = path.join(process.cwd(), 'error_log.txt');
      fs.writeFileSync(logPath, fullError, 'utf-8');
      console.log(`\n🛡️ Guardian Reporter: FULL error dump saved to ${logPath}`);
    }
  }
}

export default GuardianReporter;
