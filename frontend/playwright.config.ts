import { defineConfig, devices } from '@playwright/test'


const frontendUrl = process.env.E2E_BASE_URL ?? 'http://localhost:5173'
const backendUrl = process.env.E2E_API_ORIGIN ?? 'http://127.0.0.1:8000'
const databaseAdminUrl = process.env.E2E_DATABASE_ADMIN_URL
  ?? process.env.TEST_DATABASE_ADMIN_URL
  ?? 'postgresql+psycopg://campo_logistica:change_me_for_local_development@127.0.0.1:55432/postgres'

export default defineConfig({
  testDir: './e2e',
  globalTeardown: './e2e/global-teardown.ts',
  fullyParallel: false,
  forbidOnly: true,
  workers: 1,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
  ],
  use: {
    baseURL: frontendUrl,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
    ...devices['Desktop Edge'],
    channel: 'msedge',
  },
  webServer: [
    {
      command: '.\\.venv\\Scripts\\python.exe -m tests.e2e_server serve',
      cwd: '../backend',
      env: {
        E2E_DATABASE_ADMIN_URL: databaseAdminUrl,
        FRONTEND_ORIGIN: frontendUrl,
      },
      url: `${backendUrl}/health`,
      // Never reuse port 8000: the E2E server owns an isolated database.
      reuseExistingServer: true,
      timeout: 60_000,
    },
    {
      command: 'npm run dev -- --host localhost --port 5173',
      cwd: '.',
      env: {
        VITE_API_URL: `${backendUrl}/api/v1`,
      },
      url: frontendUrl,
      reuseExistingServer: true,
      timeout: 60_000,
    },
  ],
})
