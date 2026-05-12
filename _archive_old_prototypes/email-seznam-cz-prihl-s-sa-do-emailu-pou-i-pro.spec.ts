import { Page } from '@playwright/test';

export class BasePage {
  readonly page: Page;
  constructor(page: Page) { this.page = page; }
}

export class EmailPage extends BasePage {
  get emailInput() { return this.page.getByPlaceholder(/e-mail/i).first(); }
  get continueButton() { return this.page.getByRole('button', { name: 'Pokračovat' }).first(); }
  get passwordInput() { return this.page.locator('#login-password'); }
  get loginButton() { return this.page.getByRole('button', { name: 'Přihlásit' }).first(); }
  get composeButton() { return this.page.getByRole('button', { name: 'Nová zpráva' }).first(); }
  get toInput() { return this.page.getByPlaceholder(/komu/i).first(); }
  get subjectInput() { return this.page.getByPlaceholder(/předmět/i).first(); }
  get messageInput() { return this.page.getByPlaceholder(/zpráva/i).first(); }
  get fileInput() { return this.page.getByRole('button', { name: 'Přiložit soubor' }).first(); }
  get sendButton() { return this.page.getByRole('button', { name: 'Odeslat' }).first(); }
  get successMessage() { return this.page.getByText(/zpráva odeslána/i).first(); }
}

export class LoginPage extends BasePage {
  get emailInput() { return this.page.getByPlaceholder(/e-mail/i).first(); }
  get continueButton() { return this.page.getByRole('button', { name: 'Pokračovat' }).first(); }
  get passwordInput() { return this.page.locator('#login-password'); }
  get loginButton() { return this.page.getByRole('button', { name: 'Přihlásit' }).first(); }
}