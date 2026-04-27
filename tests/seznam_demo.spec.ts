import { test, expect } from './fixtures';

// 🚨 Pridali sme .only, aby sa spustil len tento test
test.only('Seznam Login - AI Healing Test', async ({ page }) => {
    await page.goto('https://login.szn.cz/');
    console.log('🤖 Pokúšam sa zadať email...');

    // 🚨 SABOTÁŽ: Neexistujúci lokátor, z ktorého ale jasne kričí zámer (chceme zadať email)
    await page.locator('input#login-username').fill('milos.tester@seznam.cz');

    await page.locator('button[type="submit"]').click();
});