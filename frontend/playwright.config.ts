import { defineConfig, devices } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './playwright',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:8080',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Capture screenshot on failure */
    screenshot: 'only-on-failure',

    /* Capture video on failure */
    video: 'retain-on-failure',

    /* Custom timeout for actions */
    actionTimeout: 10000,

    /* Custom timeout for navigation */
    navigationTimeout: 15000,
  },

  /* Configure projects for major browsers */
  projects: [
    // Setup project - authenticates user and saves state
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
      teardown: 'cleanup',
    },

    // Cleanup project
    {
      name: 'cleanup', 
      testMatch: /.*\.cleanup\.ts/,
    },

    // Main test projects with different browser contexts
    {
      name: 'chromium-auth-flow',
      use: { 
        ...devices['Desktop Chrome'],
        // Don't use stored auth for auth flow tests
        storageState: { cookies: [], origins: [] }
      },
      testMatch: /auth-flow\.test\.ts/,
      dependencies: ['setup'],
    },

    {
      name: 'chromium-authenticated',
      use: { 
        ...devices['Desktop Chrome'],
        // Use prepared auth state for authenticated tests
        storageState: path.join(__dirname, 'playwright/.auth/user.json'),
      },
      testMatch: /(?!auth-flow).*\.test\.ts/,
      dependencies: ['setup'],
    },

    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        storageState: path.join(__dirname, 'playwright/.auth/user.json'),
      },
      testMatch: /ui-components\.test\.ts/,
      dependencies: ['setup'],
    },

    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        storageState: path.join(__dirname, 'playwright/.auth/user.json'),
      },
      testMatch: /ui-components\.test\.ts/,
      dependencies: ['setup'],
    },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        storageState: path.join(__dirname, 'playwright/.auth/user.json'),
      },
      testMatch: /ui-components\.test\.ts/,
      dependencies: ['setup'],
    },

    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 12'],
        storageState: path.join(__dirname, 'playwright/.auth/user.json'),
      },
      testMatch: /ui-components\.test\.ts/,
      dependencies: ['setup'],
    },

    /* Security testing project without authentication */
    {
      name: 'security-tests',
      use: {
        ...devices['Desktop Chrome'],
        storageState: { cookies: [], origins: [] }
      },
      testMatch: /security\.test\.ts/,
    },
  ],

  /* Global setup and teardown */
  globalSetup: path.resolve(__dirname, './playwright/global-setup.ts'),
  globalTeardown: path.resolve(__dirname, './playwright/global-teardown.ts'),

  /* Run your local dev server before starting the tests */
  webServer: [
    {
      command: 'cd .. && make up',
      port: 8080,
      timeout: 120 * 1000,
      reuseExistingServer: !process.env.CI,
      env: {
        NODE_ENV: 'test',
      },
    },
  ],
});