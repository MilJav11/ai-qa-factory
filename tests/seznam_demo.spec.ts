import { test, expect } from './fixtures';

// 🚨 Pridali sme .only, aby sa spustil len tento test
test('Seznam Login - AI Healing Test', async ({ page }) => {
    await page.goto('https://login.szn.cz/');
    console.log('🤖 Pokúšam sa zadať email...');

    // 🚨 SABOTÁŽ: Neexistujúci lokátor, z ktorého ale jasne kričí zámer (chceme zadať email)
    await page.locator('input#login-username').fill('milos.tester@seznam.cz');

    await page.locator('form.login button[type="submit"]').click();
});