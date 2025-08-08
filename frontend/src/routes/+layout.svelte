<script lang="ts">
	import type { LayoutData } from './$types';

	export const data: LayoutData = {};
</script>

<slot />

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
		line-height: 1.5;
	}

	:global(*) {
		box-sizing: border-box;
	}
</style>
