import { test, expect } from '@playwright/test';

test.describe('UI Components and Styling', () => {
  test.describe('Login Page UI', () => {
    // Reset storage state for login page tests
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should display proper login page layout', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Check main layout elements
      await expect(page.locator('.login-page')).toBeVisible();
      await expect(page.locator('.login-card')).toBeVisible();
      
      // Check form elements
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
      await expect(page.getByLabel('Email')).toBeVisible();
      await expect(page.getByLabel('Password')).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });

    test('should have proper form accessibility', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Check form labels are properly associated
      const emailInput = page.getByLabel('Email');
      const passwordInput = page.getByLabel('Password');
      
      await expect(emailInput).toHaveAttribute('type', 'email');
      await expect(emailInput).toHaveAttribute('required');
      await expect(passwordInput).toHaveAttribute('type', 'password');
      await expect(passwordInput).toHaveAttribute('required');
      
      // Check form can be navigated with keyboard
      await emailInput.focus();
      await expect(emailInput).toBeFocused();
      
      await page.keyboard.press('Tab');
      await expect(passwordInput).toBeFocused();
    });

    test('should be responsive on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('http://localhost:8080/login');
      
      // Check login card is responsive
      const loginCard = page.locator('.login-card');
      await expect(loginCard).toBeVisible();
      
      // Check form elements are properly sized for mobile
      await expect(page.getByLabel('Email')).toBeVisible();
      await expect(page.getByLabel('Password')).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });

    test('should show loading state during form submission', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Fill form with valid credentials
      await page.getByLabel('Email').fill('admin@santaserver.dev');
      await page.getByLabel('Password').fill('admin123!');
      
      // Submit form and check for loading state
      const submitButton = page.getByRole('button', { name: /sign in/i });
      await submitButton.click();
      
      // Check for loading indicator (spinner or disabled button)
      // Note: This depends on implementation details
      await expect(submitButton).toBeDisabled({ timeout: 1000 });
    });
  });

  test.describe('Navigation UI', () => {
    // Use authenticated state for navigation tests
    test.use({ storageState: 'tests/playwright/.auth/user.json' });

    test('should display proper navigation layout', async ({ page }) => {
      await page.goto('http://localhost:8080/dashboard');
      
      // Check navigation elements
      await expect(page.locator('.navbar')).toBeVisible();
      await expect(page.getByText(/santaserver/i)).toBeVisible(); // Brand name
      
      // Check user menu elements
      await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
    });

    test('should have accessible navigation', async ({ page }) => {
      await page.goto('http://localhost:8080/dashboard');
      
      // Check navigation has proper ARIA labels
      const nav = page.locator('nav');
      await expect(nav).toBeVisible();
      
      // Check logout button is accessible
      const logoutButton = page.getByRole('button', { name: /logout/i });
      await expect(logoutButton).toBeVisible();
      
      // Test keyboard navigation
      await logoutButton.focus();
      await expect(logoutButton).toBeFocused();
    });

    test('should be responsive in mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('http://localhost:8080/dashboard');
      
      // Navigation should be visible and functional on mobile
      await expect(page.locator('.navbar')).toBeVisible();
      await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
    });
  });

  test.describe('Dashboard UI', () => {
    // Use authenticated state for dashboard tests
    test.use({ storageState: 'tests/playwright/.auth/user.json' });

    test('should display dashboard layout', async ({ page }) => {
      await page.goto('http://localhost:8080/dashboard');
      
      // Check main dashboard elements
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
      await expect(page.locator('.dashboard-layout')).toBeVisible();
      
      // Check for main content area
      await expect(page.locator('main')).toBeVisible();
    });

    test('should have proper semantic structure', async ({ page }) => {
      await page.goto('http://localhost:8080/dashboard');
      
      // Check for proper heading hierarchy
      const h1 = page.locator('h1');
      await expect(h1).toBeVisible();
      
      // Check for main landmark
      const main = page.locator('main');
      await expect(main).toBeVisible();
      
      // Check for navigation landmark
      const nav = page.locator('nav');
      await expect(nav).toBeVisible();
    });
  });

  test.describe('Error Handling UI', () => {
    // Reset storage state for error testing
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should display error messages properly', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Submit form with invalid credentials
      await page.getByLabel('Email').fill('invalid@example.com');
      await page.getByLabel('Password').fill('wrongpassword');
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Check for error message display
      const errorMessage = page.getByText(/invalid.*credential/i);
      await expect(errorMessage).toBeVisible({ timeout: 5000 });
      
      // Error should have proper styling (Bootstrap alert class)
      await expect(errorMessage).toHaveClass(/alert/);
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // Intercept network requests to simulate failure
      await page.route('**/api/v1/auth/login', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal server error' })
        });
      });

      await page.goto('http://localhost:8080/login');
      
      // Submit form
      await page.getByLabel('Email').fill('admin@santaserver.dev');
      await page.getByLabel('Password').fill('admin123!');
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Should show error message
      await expect(page.getByText(/error/i)).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('CSS and Styling', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should load Bootstrap styles correctly', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Check that Bootstrap classes are applied and working
      const card = page.locator('.card');
      await expect(card).toBeVisible();
      
      const button = page.getByRole('button', { name: /sign in/i });
      await expect(button).toHaveClass(/btn/);
      
      const form = page.locator('form');
      await expect(form).toBeVisible();
    });

    test('should have consistent color scheme', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Check custom CSS variables are loaded
      const bodyStyles = await page.evaluate(() => {
        return window.getComputedStyle(document.body);
      });
      
      // Verify some basic styling is applied
      expect(bodyStyles.fontFamily).toContain('sans-serif');
    });

    test('should maintain visual consistency across browsers', async ({ page, browserName }) => {
      await page.goto('http://localhost:8080/login');
      
      // Take screenshot for visual regression testing
      await expect(page).toHaveScreenshot(`login-page-${browserName}.png`);
    });
  });
});