import { test, expect, Page } from '@playwright/test';

// Base Page pre zdieľanú logiku
export class BasePage {
  readonly page: Page;
  constructor(page: Page) { this.page = page; }
}

// POM pre konkrétnu stránku s camelCase gettrami a .first() poistkou
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

test.describe('E2E Business Flow', () => {
  let romotorsPage: RomotorsPage;

  test.beforeEach(async ({ page }) => {
    romotorsPage = new RomotorsPage(page);
    await page.goto('https://romotors.ie');
  });

  test('should execute the contact form scenario successfully', async ({ page }) => {
    // Zablokovanie reálneho odoslania formulára (Network Mocking pre WPCF7)
    await page.route('**/contact-forms/**/feedback', async route => {
      console.log('Zachytený request formulára - BLOKUJEM odoslanie na server.');
      // Simulujeme úspešnú odpoveď od servera, aby UI ukázalo zelenú hlášku
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

    // 1. Kliknutie na tlačidlo Contact Us
    await romotorsPage.contactUsButton.click();

    // 2. Vyplnenie kontaktného formulára
    await romotorsPage.fillContactForm('Miloš Tester', 'milos.tester@example.com', '0900123456', 'Kúpa auta TEST', 'Ahojte, len Vám automaticky testujem stránku, pozdravuje MIloš.');

    // 3. Overenie, že sa tlačidlo Odoslať dá kliknúť
    await expect(romotorsPage.submitButton).toBeEnabled();

    // 4. Zaškrtnutie podmienok
    await romotorsPage.privacyPolicyCheckbox.click();

    // 5. Kliknutie na tlačidlo Odoslať
    await romotorsPage.submitContactForm();
  });
});