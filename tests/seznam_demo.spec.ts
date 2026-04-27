import { test, expect } from './fixtures';

// 🚨 Pridali sme .only
test.only('Seznam Login - AI Healing Test', async ({ page }) => {
    await page.goto('https://login.szn.cz/');
    console.log('🤖 Pokúšam sa zadať email...');
    await page.locator('#login-username').fill('milos.tester@seznam.cz');
    await page.locator('button[type="submit"]').click();
});