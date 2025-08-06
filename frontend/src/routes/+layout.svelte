<script lang="ts">
	import type { LayoutData } from './$types';

	export let data: LayoutData;
</script>

<svelte:head>
	<title>SantaServer - Enterprise Santa Management</title>
</svelte:head>

<main>
	<header>
		<h1>SantaServer</h1>
		<nav>
			<a href="/">Dashboard</a>
			<a href="/approvals">Approvals</a>
			<a href="/rules">Rules</a>
			<a href="/admin">Admin</a>
		</nav>
	</header>
	
	<slot />
</main>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	main {
		min-height: 100vh;
		background: #f5f5f5;
	}

	header {
		background: #2563eb;
		color: white;
		padding: 1rem 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	h1 {
		margin: 0;
		font-size: 1.5rem;
	}

	nav {
		display: flex;
		gap: 1rem;
	}

	nav a {
		color: white;
		text-decoration: none;
		padding: 0.5rem 1rem;
		border-radius: 0.25rem;
		transition: background-color 0.2s;
	}

	nav a:hover {
		background-color: rgba(255, 255, 255, 0.1);
	}
</style>