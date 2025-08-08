import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function globalTeardown(config: FullConfig) {
  console.log('Starting global teardown...');
  
  // Clean up authentication files if desired
  const authDir = path.join(__dirname, '.auth');
  
  try {
    if (fs.existsSync(authDir)) {
      // In CI, we might want to clean up auth files
      if (process.env.CI) {
        const files = fs.readdirSync(authDir);
        for (const file of files) {
          fs.unlinkSync(path.join(authDir, file));
        }
        fs.rmdirSync(authDir);
        console.log('Cleaned up authentication files');
      } else {
        console.log('Keeping authentication files for local development');
      }
    }
  } catch (error) {
    console.warn('Error during teardown cleanup:', error);
  }
  
  console.log('Global teardown completed');
}

export default globalTeardown;