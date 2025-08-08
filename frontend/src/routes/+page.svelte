<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated, isLoading } from '$lib/auth/stores';
	import { authActions } from '$lib/auth/api';

	onMount(async () => {
		// Initialize auth and redirect to appropriate page
		await authActions.initializeAuth();

		if ($isAuthenticated) {
			goto('/dashboard');
		} else {
			goto('/login');
		}
	});

	// Watch for authentication state changes
	$: if (!$isLoading) {
		if ($isAuthenticated) {
			goto('/dashboard');
		} else {
			goto('/login');
		}
	}
</script>

<svelte:head>
	<title>SantaServer - Enterprise Santa Management</title>
</svelte:head>

{#if $isLoading}
	<div class="bg-gradient-dark min-vh-100 d-flex flex-column align-items-center justify-content-center text-white">
		<div class="spinner-border text-light" style="width: 3rem; height: 3rem;" role="status">
			<span class="visually-hidden">Loading...</span>
		</div>
		<p class="mt-3">Loading SantaServer...</p>
	</div>
{/if}
