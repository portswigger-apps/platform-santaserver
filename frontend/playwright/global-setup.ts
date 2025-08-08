import { chromium, FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function globalSetup(config: FullConfig) {
  console.log('Starting global setup...');
  
  // Create .auth directory if it doesn't exist
  const authDir = path.join(__dirname, '.auth');
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
    console.log('Created .auth directory');
  }

  // Ensure the web server is up before running tests
  const baseURL = config.use?.baseURL || 'http://localhost:8080';
  
  // Launch browser for health check
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Wait for server to be ready
    let retries = 30;
    let serverReady = false;
    
    while (retries > 0 && !serverReady) {
      try {
        const response = await page.goto(`${baseURL}/health`);
        if (response?.ok()) {
          serverReady = true;
          console.log('Server is ready for testing');
        }
      } catch (error) {
        console.log(`Waiting for server to be ready... ${retries} retries left`);
        await page.waitForTimeout(2000);
        retries--;
      }
    }
    
    if (!serverReady) {
      throw new Error('Server failed to start within expected time');
    }
    
    // Verify database is accessible by checking login endpoint
    try {
      const response = await page.request.get(`${baseURL}/api/v1/health`);
      if (!response.ok()) {
        console.warn('API health check failed, but continuing with tests');
      }
    } catch (error) {
      console.warn('API health check error:', error);
    }
    
  } finally {
    await browser.close();
  }
  
  console.log('Global setup completed successfully');
}

export default globalSetup;