import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Base Page pre zdieľanú logiku
export class BasePage {
  readonly page: Page;
  constructor(page: Page) { this.page = page; }
}

// POM pre konkrétnu stránku
export class RomotorsPage extends BasePage {
  get contactUsButton() { return this.page.getByRole('link', { name: /contact us/i }).first(); }
  get contactNameInput() { return this.page.getByPlaceholder(/name/i).first(); }
  get contactEmailInput() { return this.page.getByPlaceholder(/email/i).first(); }
  get contactPhoneInput() { return this.page.getByPlaceholder(/phone/i).first(); }
  get contactSubjectInput() { return this.page.getByPlaceholder(/subject/i).first(); }
  get contactMessageInput() { return this.page.getByPlaceholder(/help you/i).first(); }
  get submitButton() { return this.page.getByRole('button', { name: /get in touch/i }).first(); }
  get privacyPolicyCheckbox() { return this.page.locator('span.wpcf7-list-item-label', { hasText: /I agree/i }).first(); }

  // Komplexná biznis akcia
  async fillContactForm(name: string, email: string, phone: string, subject: string, message: string) {
    await this.contactNameInput.fill(name);
    await this.contactEmailInput.fill(email);
    await this.contactPhoneInput.fill(phone);
    await this.contactSubjectInput.fill(subject);
    await this.contactMessageInput.fill(message);
  }

  async submitContactForm() {
    await this.submitButton.click();
  }
}

// Načítanie a jednoduché parsovanie CSV
const csvPath = path.resolve(__dirname, 'test_data', 'contacts.csv');
const csvData = fs.readFileSync(csvPath, 'utf8');

const records = csvData.split('\n')
  .filter(line => line.trim().length > 0)
  .slice(1) // Preskočíme hlavičku
  .map(line => {
    const parts = line.split(',');
    return {
      name: parts[0],
      email: parts[1],
      phone: parts[2],
      subject: parts[3],
      // Zvyšok spojíme, ak správa obsahuje čiarku a odstránime CSV úvodzovky z extrémnych test-casov
      message: parts.slice(4).join(',').replace(/^"|"$/g, '').trim()
    };
  });

test.describe('Data-Driven E2E Business Flow', () => {
  for (const record of records) {
    // Generovanie unikátneho testu pre každý riadok v CSV
    test(`Form submission for: ${record.name || 'Empty Name'}`, async ({ page }) => {
      const romotorsPage = new RomotorsPage(page);
      
      // Zablokovanie reálneho odoslania formulára - Mocking (WPCF7)
      await page.route('**/contact-forms/**/feedback', async route => {
        console.log(`[Mock] Zastavené odosielanie formu na server. Email: ${record.email}`);
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            into: "#",
            status: "mail_sent",
            message: "Thank you for your message. It has been sent."
          })
        });
      });

      await page.goto('https://romotors.ie');

      // 1. Kliknutie na tlačidlo Contact Us
      await romotorsPage.contactUsButton.click();

      // 2. Vyplnenie formulára z CSV dát
      await romotorsPage.fillContactForm(
        record.name,
        record.email,
        record.phone,
        record.subject,
        record.message
      );

      // 3. Overenie pripravenosti tlačidla
      await expect(romotorsPage.submitButton).toBeEnabled();

      // 4. Úspešné zaškrtnutie podmienok (pomocou upraveného visual štandardu)
      await romotorsPage.privacyPolicyCheckbox.click();

      // 5. Odoslanie (realita je prebratá naším Network routerom)
      await romotorsPage.submitContactForm();
    });
  }
});
