import { test, expect } from './fixtures';

test('Add new todo item', async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc/');

  const input = page.locator('input.new-todo');
  await input.fill('Pass the QA interview');
  await input.press('Enter');

  await expect(page.locator('[data-testid="todo-item"]')).toContainText('Pass the QA interview');
});