import { expect, test } from '@playwright/test';

test('checkout completes with healthy environment, valid data and correct total', async ({ page }, testInfo) => {
  const networkFailures: Array<Record<string, unknown>> = [];
  const consoleErrors: Array<Record<string, unknown>> = [];
  page.on('response', async (response) => {
    if (response.status() >= 400) {
      networkFailures.push({
        method: response.request().method(),
        url: response.url(),
        status_code: response.status(),
        correlation_id: await response.headerValue('x-correlation-id'),
      });
    }
  });
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push({ level: 'error', message: message.text() });
  });

  await page.goto('/');
  const health = await page.request.get('/health');
  expect(health.status()).toBe(200);
  const session = await page.request.get('/api/session');
  expect(session.status()).toBe(200);
  await expect(page.locator('#account')).toHaveText('Account active');
  await expect(page.locator('#total')).toHaveText('£100');
  await page.getByRole('button', { name: 'Checkout' }).click();
  await expect(page.locator('#result')).toHaveText('Order confirmed', { timeout: 1_000 });

  await testInfo.attach('triage-metadata', {
    body: JSON.stringify({ networkFailures, consoleErrors, pageUrl: page.url() }),
    contentType: 'application/json',
  });
});

