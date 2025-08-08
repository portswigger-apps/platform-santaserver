module.exports = {
	root: true,
	extends: ['eslint:recommended', 'prettier'],
	parser: '@typescript-eslint/parser',
	plugins: ['@typescript-eslint'],
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 2020
	},
	env: {
		browser: true,
		es2017: true,
		node: true
	},
	overrides: [
		{
			files: ['*.ts', '*.tsx'],
			extends: ['plugin:@typescript-eslint/recommended'],
			rules: {
				'@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
				'@typescript-eslint/explicit-function-return-type': 'off',
				'@typescript-eslint/explicit-module-boundary-types': 'off'
			}
		}
	],
	ignorePatterns: ['.svelte-kit/', 'build/', 'dist/', '*.svelte']
};
