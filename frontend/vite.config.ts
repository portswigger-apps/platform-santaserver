import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 3000,
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true
			}
		}
	},
	css: {
		preprocessorOptions: {
			scss: {
				// Suppress deprecation warnings from Bootstrap's internal @import usage
				// These will be resolved when Bootstrap v6 is released
				quietDeps: true,
				// Suppress legacy warnings
				silenceDeprecations: ['legacy-js-api']
			}
		}
	}
});
