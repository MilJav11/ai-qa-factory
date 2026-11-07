import { test, expect, Page } from '@playwright/test';

export class BasePage {
  readonly page: Page;
  constructor(page: Page) { this.page = page; }
}

export class PrihlasovaniePage extends BasePage {
  get emailInput() { return this.page.getByPlaceholder('').first(); }
  get hesloInput() { return this.page.getByPlaceholder('Heslo').first(); }
  get jazykSelect() { return this.page.getByRole('combobox').first(); }
  get poslatButton() { return this.page.getByRole('button', { name: 'Odeslat' }).first(); }
  get attachmentInput() { return this.page.locator('input[type="file"]').first(); }
  get subjectInput() { return this.page.getByPlaceholder('Předmět').first(); }
  get textArea() { return this.page.getByPlaceholder(/Napište zprávu/i).first(); }

  async vyplnEmail() {
    await this.emailInput.fill(process.env.SEZNAM_EMAIL);
    await this.emailInput.press('Enter');
  }

  async vyplnHeslo() {
    await this.page.locator('#login-password').fill(process.env.SEZNAM_PASSWORD as string);
    await this.page.locator('#login-password').press('Enter');
  }

  async vytvorNovyMail() {
    // 1. Zrušenie cookies/reklám (tvoj try/except blok)
    try {
      await this.page.getByTestId('cw-button-agree-with-ads').click({ timeout: 3000 });
    } catch (e) {
      // Ignorujeme, ak tam reklama zrovna nie je
    }

    // Tvoja poistka: Čakáme na úplné načítanie siete po logine
    await this.page.waitForLoadState('networkidle');

    // 2. Klik na Napsat e-mail (tvoj spoľahlivý multi-selektor)
    await this.page.locator('a[href*="compose"], :text-is("Napsat e-mail"), :text-is("Nová zpráva")').first().click();

    await this.page.waitForTimeout(500); // Ľudská pauza

    // 3. Komu
    await this.page.getByRole('textbox', { name: 'Komu…' }).fill('user@example.com');

    await this.page.waitForTimeout(500);

    // 4. Predmet
    await this.page.getByRole('textbox', { name: 'Předmět:' }).fill('Ostrý AI Test z Python Blueprintu');

    await this.page.waitForTimeout(500);

    // 5. Telo správy (Tvoj presný .area selektor)
    await this.page.locator('.area').first().fill('Ahoj,\n\nToto je test poslaný vďaka tvojmu starému Python kódu.\n\nMiloš');

    // 6. Príloha (Tvoj File Chooser z Pythonu preložený do TypeScriptu!)
    const fileChooserPromise = this.page.waitForEvent('filechooser');
    await this.page.getByRole('button', { name: 'Přiložit soubory' }).click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles('test_data/priloha.txt');

    // Tvoj kritický slowdown na nahratie prílohy
    await this.page.waitForTimeout(3000);

    // 7. Odoslanie
    await this.page.waitForTimeout(1000);
    await this.page.getByRole('button', { name: 'Odeslat e‑mail' }).click();
  }

  async pridajPrilohu() {
    await this.attachmentInput.setInputFiles('test_data/priloha.txt');
  }

  async odesliMail() {
    await this.poslatButton.click();
    await this.page.waitForSelector('text="Zpráva byla odeslána."');
  }
}

test.describe('Prihlasovanie Page Tests', () => {
  let prihlasovaniePage: PrihlasovaniePage;
  test.beforeEach(async ({ page }) => {
    prihlasovaniePage = new PrihlasovaniePage(page);
    await page.goto('https://email.seznam.cz');
  });

  test('should verify basic UI elements are attached or visible', async () => {
    await expect(prihlasovaniePage.emailInput).toBeVisible();
  });

  test('should login and send email', async () => {

    await prihlasovaniePage.vyplnEmail();
    await prihlasovaniePage.vyplnHeslo();
    await prihlasovaniePage.vytvorNovyMail();

    // 🏆 Finálna kontrola víťazstva
    await expect(prihlasovaniePage.page.locator('text="E‑mail byl úspěšně odeslán."')).toBeVisible({ timeout: 10000 });

  });
});