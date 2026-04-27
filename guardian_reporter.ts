import { Reporter, TestCase, TestResult } from '@playwright/test/reporter';
import * as fs from 'fs';
import * as path from 'path';

class GuardianReporter implements Reporter {
  onTestEnd(test: TestCase, result: TestResult) {
    if (result.status === 'failed' || result.status === 'timedOut') {
      // 🚨 ZMENA: Prejdeme úplne všetky detaily chyby, ktoré Playwright zachytil
      let fullError = result.errors.map(err => err.stack || err.message).join('\n\n');
      
      // Ak by bolo pole errors prázdne, skúsime aspoň základný error
      if (!fullError && result.error) {
        fullError = result.error.stack || result.error.message || 'No error message';
      }

      // Vyčistíme ANSI escape kódy (farby)
      fullError = fullError.replace(/\x1b\[[0-9;]*m/g, '');

      const logPath = path.join(process.cwd(), 'error_log.txt');
      fs.writeFileSync(logPath, fullError, 'utf-8');
      console.log(`\n🛡️ Guardian Reporter: BRUTÁLNY DUMP chyby uložený do ${logPath}`);
    }
  }
}

export default GuardianReporter;
