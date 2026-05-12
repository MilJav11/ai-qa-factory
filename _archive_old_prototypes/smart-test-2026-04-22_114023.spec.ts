// page-object.ts
import { Page } from 'playwright';

export class EmailPage {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  get loginUsernameInput() {
    return this.page.locator('#login-username');
  }

  get loginPasswordInput() {
    return this.page.locator('#login-password');
  }

  async login(username: string, password: string) {
    await this.loginUsernameInput.fill(username);
    await this.loginPasswordInput.fill(password);
    // Since the submit button does not have an ID, we will use the first submit button
    await this.page.locator('button[type="submit"]').first().click();
  }
}

// test.ts
import { test, expect } from '@playwright/test';
import { EmailPage } from './page-object';

test('login test', async ({ page }) => {
  const emailPage = new EmailPage(page);
  await page.goto('https://email.seznam.cz');
  await emailPage.login(process.env.SEZNAM_EMAIL, process.env.SEZNAM_PASSWORD);
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
});