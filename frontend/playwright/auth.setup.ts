import { test as setup, expect } from '@playwright/test';
import { readFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Authentication setup script that creates users and saves auth state
const authFile = path.join(__dirname, '.auth/user.json');

setup('authenticate as test user', async ({ page }) => {
  // First create a test user via API since we need valid credentials
  console.log('Setting up test user authentication...');
  
  // Navigate to login page
  await page.goto('http://localhost:8080/login');
  
  // Wait for the page to fully load
  await page.waitForLoadState('networkidle');
  
  // Check if login form is visible
  await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  
  // Fill login form with test credentials
  await page.getByLabel('Email').fill('admin@santaserver.dev');
  await page.getByLabel('Password').fill('admin123!');
  
  // Click sign in button
  await page.getByRole('button', { name: /sign in/i }).click();
  
  // Wait for successful authentication - should redirect to dashboard
  await page.waitForURL('http://localhost:8080/dashboard', { timeout: 10000 });
  
  // Verify we're authenticated by checking for dashboard content
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  
  // Verify navigation shows user is logged in
  await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
  
  console.log('Authentication successful, saving state...');
  
  // Save authentication state to file
  await page.context().storageState({ path: authFile });
  
  console.log('Authentication state saved to:', authFile);
});