import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 15_000,
  expect: { timeout: 1_000 },
  retries: process.env.FAILURE_PROFILE === 'flaky_timing' ? 1 : 0,
  reporter: [['line'], ['json', { outputFile: 'playwright-report.json' }]],
  use: {
    baseURL: 'http://127.0.0.1:4173',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'node src/server.mjs',
    url: 'http://127.0.0.1:4173/ready',
    reuseExistingServer: false,
    timeout: 10_000,
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
});

