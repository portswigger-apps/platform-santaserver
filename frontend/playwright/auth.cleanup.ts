import { test as cleanup } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

cleanup('cleanup authentication state', async () => {
  console.log('Cleaning up test authentication state...');
  
  const authFile = path.join(__dirname, '.auth/user.json');
  
  try {
    if (fs.existsSync(authFile)) {
      fs.unlinkSync(authFile);
      console.log('Cleaned up authentication state file');
    }
  } catch (error) {
    console.warn('Error cleaning up auth state:', error);
  }
  
  console.log('Authentication cleanup completed');
});