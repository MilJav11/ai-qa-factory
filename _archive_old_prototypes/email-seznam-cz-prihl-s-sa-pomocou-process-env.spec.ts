import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';

export class BasePage {
  readonly page: Page;
  constructor(page: Page) { this.page = page; }
}

export class EmailPage extends BasePage {
  get emailInput() { return this.page.getByPlaceholder('').first(); }
  get continuarButton() { return this.page.getByRole('button', { name: 'Pokračovat' }).first(); }
  get loginPasswordInput() { return this.page.getByPlaceholder(/heslo/i).first(); }
  get loginButton() { return this.page.getByRole('button', { name: 'Přihlásit' }).first(); }
  get composeButton() { return this.page.getByRole('button', { name: 'Nový e-mail' }).first(); }
  get recipientInput() { return this.page.getByPlaceholder(/komu/i).first(); }
  get subjectInput() { return this.page.getByPlaceholder(/předmět/i).first(); }
  get bodyInput() { return this.page.getByRole('textbox', { name: /tělo zprávy/i }).first(); }
  get attachFileInput() { return this.page.getByRole('button', { name: /přiložit soubor/i }).first(); }
  get sendButton() { return this.page.getByRole('button', { name: /odeslat/i }).first(); }
  get successMessage() { return this.page.getByText(/e-mail byl odeslán/i).first(); }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.continuarButton.click();
    await this.loginPasswordInput.fill(password);
    await this.loginButton.click();
  }

  async composeEmail(recipient: string, subject: string, body: string) {
    await this.composeButton.click();
    await this.recipientInput.fill(recipient);
    await this.subjectInput.fill(subject);
    await this.bodyInput.fill(body);
  }

  async attachFile(filePath: string) {
    await this.attachFileInput.click();
    await this.page.setInputFiles(this.attachFileInput, filePath);
  }

  async sendEmail() {
    await this.sendButton.click();
  }
}

test.describe('Email Page Tests', () => {
  let emailPage: EmailPage;
  test.beforeEach(async ({ page }) => {
    emailPage = new EmailPage(page);
    await page.goto('https://email.seznam.cz');
  });

  test('should login and send email', async () => {
    await emailPage.login(process.env.SEZNAM_EMAIL, process.env.SEZNAM_PASSWORD);
    await emailPage.composeEmail('dentalux11@gmail.com', 'Ostrý AI Test', 'Toto je reálny test odoslaný umelou inteligenciou');
    await emailPage.attachFile('test_data/priloha.txt');
    await emailPage.sendEmail();
    await expect(emailPage.successMessage).toBeVisible();
  });
});