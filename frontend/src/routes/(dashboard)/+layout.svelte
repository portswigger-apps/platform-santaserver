<!-- src/routes/(dashboard)/+layout.svelte -->
<script>
	import AuthGuard from '$lib/components/layout/AuthGuard.svelte';
	import Navigation from '$lib/components/layout/Navigation.svelte';
</script>

<AuthGuard>
	<div class="dashboard-layout">
		<Navigation />
		<main class="main-content">
			<slot />
		</main>
	</div>
</AuthGuard>

<style>
	.dashboard-layout {
		min-height: 100vh;
		background-color: #f8fafc;
	}

	.main-content {
		min-height: calc(100vh - 80px); /* Adjust based on navigation height */
		padding: 0;
	}

	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
	}
</style>
