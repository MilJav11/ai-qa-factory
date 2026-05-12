// page-object.ts
import { Page } from 'playwright';

export class EmailPage {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  get emailInput() {
    return this.page.locator('#login-username');
  }

  get passwordInput() {
    return this.page.locator('input[type="password"]');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.page.keyboard.press('Enter');
    await this.passwordInput.fill(password);
    await this.page.keyboard.press('Enter');
  }
}

// email.spec.ts
import { test, expect } from '@playwright/test';
import { EmailPage } from './page-object';

test('login to email', async ({ page }) => {
  const emailPage = new EmailPage(page);
  await page.goto('https://email.seznam.cz');
  await emailPage.login(process.env.SEZNAM_EMAIL, 'your_password');
  await expect(page.url()).toContain('https://email.seznam.cz/');
});