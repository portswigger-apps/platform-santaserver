import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.describe('Unauthenticated Access', () => {
    // Reset storage state for these tests to ensure no authentication
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should redirect to login when accessing root', async ({ page }) => {
      await page.goto('http://localhost:8080/');
      
      // Should redirect to login page
      await expect(page).toHaveURL(/.*\/login/);
      
      // Should see login form
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
      await expect(page.getByLabel('Email')).toBeVisible();
      await expect(page.getByLabel('Password')).toBeVisible();
      await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    });

    test('should redirect to login when accessing protected dashboard', async ({ page }) => {
      await page.goto('http://localhost:8080/dashboard');
      
      // Should redirect to login with return URL
      await expect(page).toHaveURL(/.*\/login\?redirect=.*dashboard/);
      
      // Should see login form
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    });

    test('should allow direct access to login page', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Should stay on login page
      await expect(page).toHaveURL('http://localhost:8080/login');
      
      // Should see login form elements
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
      await expect(page.getByLabel('Email')).toBeVisible();
      await expect(page.getByLabel('Password')).toBeVisible();
    });
  });

  test.describe('Login Process', () => {
    // Reset storage state for these tests
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should show validation errors for empty form', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Click submit without filling form
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Should show validation errors (assuming client-side validation)
      // Note: Actual validation behavior depends on implementation
      await expect(page.getByLabel('Email')).toHaveAttribute('required');
      await expect(page.getByLabel('Password')).toHaveAttribute('required');
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Fill form with invalid credentials
      await page.getByLabel('Email').fill('invalid@example.com');
      await page.getByLabel('Password').fill('wrongpassword');
      
      // Submit form
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Should show error message
      await expect(page.getByText(/invalid.*credential/i)).toBeVisible({ timeout: 5000 });
      
      // Should remain on login page
      await expect(page).toHaveURL(/.*\/login/);
    });

    test('should successfully login with valid credentials', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Fill form with valid credentials
      await page.getByLabel('Email').fill('admin@santaserver.dev');
      await page.getByLabel('Password').fill('admin123!');
      
      // Submit form
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Should redirect to dashboard
      await expect(page).toHaveURL('http://localhost:8080/dashboard', { timeout: 10000 });
      
      // Should see dashboard content
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
      
      // Should see navigation with logout button
      await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
    });

    test('should redirect to original destination after login', async ({ page }) => {
      // Try to access dashboard while not authenticated
      await page.goto('http://localhost:8080/dashboard');
      
      // Should redirect to login with return URL
      await expect(page).toHaveURL(/.*\/login\?redirect=.*dashboard/);
      
      // Login with valid credentials
      await page.getByLabel('Email').fill('admin@santaserver.dev');
      await page.getByLabel('Password').fill('admin123!');
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Should redirect back to dashboard
      await expect(page).toHaveURL('http://localhost:8080/dashboard', { timeout: 10000 });
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    });
  });

  test.describe('Authenticated Navigation', () => {
    // Use authenticated state for these tests
    test.use({ storageState: 'tests/playwright/.auth/user.json' });

    test('should allow access to dashboard when authenticated', async ({ page }) => {
      await page.goto('http://localhost:8080/dashboard');
      
      // Should stay on dashboard
      await expect(page).toHaveURL('http://localhost:8080/dashboard');
      
      // Should see dashboard content
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
      
      // Should see authenticated navigation
      await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
    });

    test('should redirect authenticated users away from login', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Should redirect to dashboard
      await expect(page).toHaveURL('http://localhost:8080/dashboard');
      
      // Should see dashboard content
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    });

    test('should allow access to root when authenticated', async ({ page }) => {
      await page.goto('http://localhost:8080/');
      
      // Should redirect to dashboard or show authenticated content
      await expect(page).toHaveURL('http://localhost:8080/dashboard');
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    });
  });

  test.describe('Logout Process', () => {
    // Use authenticated state for these tests
    test.use({ storageState: 'tests/playwright/.auth/user.json' });

    test('should successfully logout', async ({ page }) => {
      await page.goto('http://localhost:8080/dashboard');
      
      // Verify we're authenticated
      await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
      
      // Click logout button
      await page.getByRole('button', { name: /logout/i }).click();
      
      // Should redirect to login page
      await expect(page).toHaveURL(/.*\/login/, { timeout: 5000 });
      
      // Should see login form
      await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
      
      // Should not be able to access dashboard anymore
      await page.goto('http://localhost:8080/dashboard');
      await expect(page).toHaveURL(/.*\/login\?redirect=.*dashboard/);
    });
  });
});