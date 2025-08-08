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
	<div class="loading">
		<div class="spinner"></div>
		<p>Loading SantaServer...</p>
	</div>
{/if}

<style>
	.loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		color: #6b7280;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.spinner {
		width: 2rem;
		height: 2rem;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top: 2px solid white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
</style>