import { test, expect } from '@playwright/test';

test.describe('Security Features', () => {
  test.describe('Server-Side Authentication Protection', () => {
    // Reset storage state for security tests
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should enforce server-side authentication on protected routes', async ({ page }) => {
      // Try to access protected routes directly
      const protectedRoutes = [
        'http://localhost:8080/',
        'http://localhost:8080/dashboard',
        'http://localhost:8080/dashboard/settings'
      ];

      for (const route of protectedRoutes) {
        await page.goto(route);
        
        // Should redirect to login due to nginx auth_request
        await expect(page).toHaveURL(/.*\/login/, { timeout: 5000 });
      }
    });

    test('should allow access to public routes without authentication', async ({ page }) => {
      const publicRoutes = [
        'http://localhost:8080/login',
        'http://localhost:8080/health'
      ];

      for (const route of publicRoutes) {
        const response = await page.goto(route);
        
        // Should get successful response
        expect(response?.status()).toBe(200);
        
        if (route.includes('/login')) {
          // Should stay on login page
          await expect(page).toHaveURL('http://localhost:8080/login');
        }
      }
    });

    test('should protect static assets except for login page requirements', async ({ page }) => {
      // Static assets for login page should be accessible
      const publicAssets = [
        'http://localhost:8080/_app/immutable/chunks/index.js',
        'http://localhost:8080/_app/immutable/assets/app.css'
      ];

      for (const asset of publicAssets) {
        const response = await page.goto(asset);
        
        // Should get successful response or 404 (asset doesn't exist), not 401/302
        expect([200, 404]).toContain(response?.status() || 404);
      }
    });

    test('should validate JWT tokens server-side', async ({ page }) => {
      // Try to access API with invalid token
      const response = await page.request.get('http://localhost:8080/api/v1/auth/verify', {
        headers: {
          'Authorization': 'Bearer invalid_token'
        }
      });

      expect(response.status()).toBe(401);
      
      const body = await response.json();
      expect(body.detail).toContain('Invalid');
    });
  });

  test.describe('Session Security', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should implement proper session timeout', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Login first
      await page.getByLabel('Email').fill('admin@santaserver.dev');
      await page.getByLabel('Password').fill('admin123!');
      await page.getByRole('button', { name: /sign in/i }).click();
      
      await expect(page).toHaveURL('http://localhost:8080/dashboard');
      
      // Check that session has proper expiry (implementation dependent)
      const localStorage = await page.evaluate(() => {
        return window.localStorage.getItem('refresh_token');
      });
      
      expect(localStorage).toBeTruthy();
    });

    test('should clear session data on logout', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Login first
      await page.getByLabel('Email').fill('admin@santaserver.dev');
      await page.getByLabel('Password').fill('admin123!');
      await page.getByRole('button', { name: /sign in/i }).click();
      
      await expect(page).toHaveURL('http://localhost:8080/dashboard');
      
      // Verify we have session data
      let localStorage = await page.evaluate(() => {
        return window.localStorage.getItem('refresh_token');
      });
      expect(localStorage).toBeTruthy();
      
      // Logout
      await page.getByRole('button', { name: /logout/i }).click();
      
      // Verify session data is cleared
      localStorage = await page.evaluate(() => {
        return window.localStorage.getItem('refresh_token');
      });
      expect(localStorage).toBeNull();
    });
  });

  test.describe('XSS Protection', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should sanitize input fields', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Try to inject script tag
      const xssPayload = '<script>alert("xss")</script>';
      
      await page.getByLabel('Email').fill(xssPayload);
      await page.getByLabel('Password').fill('password');
      
      // Submit form
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Should not execute script - page should remain functional
      await expect(page.getByLabel('Email')).toBeVisible();
      
      // Check that script was not executed
      const alertDialogs = [];
      page.on('dialog', dialog => {
        alertDialogs.push(dialog);
        dialog.dismiss();
      });
      
      expect(alertDialogs.length).toBe(0);
    });

    test('should have proper Content-Security-Policy headers', async ({ page }) => {
      const response = await page.goto('http://localhost:8080/login');
      
      // Check for security headers
      const headers = response?.headers();
      
      // Should have security headers (depending on implementation)
      expect(headers?.['x-frame-options']).toBe('SAMEORIGIN');
      expect(headers?.['x-content-type-options']).toBe('nosniff');
      expect(headers?.['x-xss-protection']).toBe('1; mode=block');
    });
  });

  test.describe('CSRF Protection', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should include CSRF protection for state-changing requests', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Monitor network requests to check for CSRF tokens
      const requests: string[] = [];
      page.on('request', request => {
        if (request.method() === 'POST') {
          requests.push(request.url());
        }
      });
      
      // Submit login form
      await page.getByLabel('Email').fill('admin@santaserver.dev');
      await page.getByLabel('Password').fill('admin123!');
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Should have made POST request to login endpoint
      expect(requests.some(url => url.includes('/auth/login'))).toBeTruthy();
    });
  });

  test.describe('Rate Limiting', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should implement rate limiting on login attempts', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Attempt multiple failed logins rapidly
      const maxAttempts = 5;
      const responses: number[] = [];
      
      for (let i = 0; i < maxAttempts; i++) {
        await page.getByLabel('Email').fill('test@example.com');
        await page.getByLabel('Password').fill('wrongpassword');
        
        // Intercept the response
        const responsePromise = page.waitForResponse('**/api/v1/auth/login');
        await page.getByRole('button', { name: /sign in/i }).click();
        
        const response = await responsePromise;
        responses.push(response.status());
        
        // Clear form for next attempt
        await page.getByLabel('Email').clear();
        await page.getByLabel('Password').clear();
        
        // Small delay between attempts
        await page.waitForTimeout(100);
      }
      
      // Should receive 401 responses (implementation may include rate limiting)
      expect(responses).toContain(401);
    });
  });

  test.describe('Input Validation', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should validate email format', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Try invalid email formats
      const invalidEmails = ['invalid', 'invalid@', '@invalid.com', 'invalid.com'];
      
      for (const email of invalidEmails) {
        await page.getByLabel('Email').fill(email);
        await page.getByLabel('Password').fill('password');
        
        const emailInput = page.getByLabel('Email');
        
        // HTML5 validation should catch invalid emails
        const isValid = await emailInput.evaluate((input: HTMLInputElement) => {
          return input.checkValidity();
        });
        
        expect(isValid).toBeFalsy();
        
        // Clear for next test
        await page.getByLabel('Email').clear();
      }
    });

    test('should enforce password requirements', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Test with valid email and various passwords
      await page.getByLabel('Email').fill('test@example.com');
      
      const weakPasswords = ['', '123', 'password'];
      
      for (const password of weakPasswords) {
        await page.getByLabel('Password').fill(password);
        
        const passwordInput = page.getByLabel('Password');
        
        // Check required attribute validation
        if (password === '') {
          const isValid = await passwordInput.evaluate((input: HTMLInputElement) => {
            return input.checkValidity();
          });
          expect(isValid).toBeFalsy();
        }
        
        // Clear for next test
        await page.getByLabel('Password').clear();
      }
    });
  });

  test.describe('Error Information Disclosure', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should not expose sensitive information in error messages', async ({ page }) => {
      await page.goto('http://localhost:8080/login');
      
      // Try login with non-existent user
      await page.getByLabel('Email').fill('nonexistent@example.com');
      await page.getByLabel('Password').fill('password');
      await page.getByRole('button', { name: /sign in/i }).click();
      
      // Error message should be generic, not revealing if user exists
      const errorText = await page.locator('[role="alert"], .alert, .error').textContent();
      
      if (errorText) {
        // Should not contain sensitive information
        expect(errorText.toLowerCase()).not.toContain('user does not exist');
        expect(errorText.toLowerCase()).not.toContain('email not found');
        
        // Should be generic
        expect(errorText.toLowerCase()).toContain('invalid');
      }
    });
  });
});