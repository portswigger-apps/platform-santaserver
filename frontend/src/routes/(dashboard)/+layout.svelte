<!-- src/routes/(dashboard)/+layout.svelte -->
<script>
	import AuthGuard from '$lib/components/layout/AuthGuard.svelte';
	import Navigation from '$lib/components/layout/Navigation.svelte';
</script>

<AuthGuard>
	<div class="min-vh-100 bg-light">
		<Navigation />
		<main>
			<slot />
		</main>
	</div>
</AuthGuard>
