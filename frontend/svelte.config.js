import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			// Generate static site
			fallback: 'index.html',
			pages: 'build',
			assets: 'build',
			strict: false
		}),
		alias: {
			$lib: 'src/lib'
		}
	}
};

export default config;
