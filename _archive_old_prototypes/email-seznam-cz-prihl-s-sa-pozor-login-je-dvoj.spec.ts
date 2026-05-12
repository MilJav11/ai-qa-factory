import { test, expect, Page } from '@playwright/test';

export class BasePage {
  readonly page: Page;
  constructor(page: Page) { this.page = page; }
}

export class LoginPage extends BasePage {
  get emailInput() { return this.page.getByPlaceholder('').first(); }
  get continueButton() { return this.page.getByRole('button', { name: 'Pokračovat' }).first(); }
  get passwordInput() { return this.page.getByPlaceholder('').first(); }
  get loginButton() { return this.page.getByRole('button', { name: 'Přihlásit se' }).first(); }
  get newEmailButton() { return this.page.getByRole('button', { name: 'Nový e-mail' }).first(); }
  get subjectInput() { return this.page.getByPlaceholder(/Předmět/i).first(); }
  get bodyInput() { return this.page.getByPlaceholder(/Napište zprávu/i).first(); }
  get fileInput() { return this.page.locator('input[type="file"]'); }
  get sendButton() { return this.page.getByRole('button', { name: 'Odeslat' }).first(); }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.continueButton.click();
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async createNewEmail(subject: string, body: string) {
    await this.newEmailButton.click();
    await this.subjectInput.fill(subject);
    await this.bodyInput.fill(body);
  }

  async attachFile(filePath: string) {
    await this.fileInput.setInputFiles(filePath);
  }

  async sendEmail() {
    await this.sendButton.click();
  }
}

test.describe('Login Page Tests', () => {
  let loginPage: LoginPage;
  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await page.goto('https://email.seznam.cz');
  });

  test('should login and send email', async () => {
    await loginPage.login(process.env.SEZNAM_EMAIL, process.env.SEZNAM_PASSWORD);
    await loginPage.createNewEmail('Ostrý AI Test', 'Reálny test');
    await loginPage.attachFile('test_data/priloha.txt');
    await loginPage.sendEmail();
    await expect(loginPage.page.getByText(/zelená hláška/i)).toBeVisible();
  });
});