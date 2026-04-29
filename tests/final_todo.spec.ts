import { test, expect } from './fixtures';

test.only('TodoMVC - pridanie úlohy', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/');

  const inputField = page.locator('input.new-todo');
  await inputField.click();
  await inputField.fill('Kupit pivo na oslavu');
  await inputField.press('Enter');

  const todoItem = page.locator('.todo-list li').filter({ hasText: 'Kupit pivo na oslavu' });
  await expect(todoItem).toBeVisible();
});