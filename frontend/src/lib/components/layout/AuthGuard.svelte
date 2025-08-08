<!-- src/lib/components/layout/AuthGuard.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { isAuthenticated, isLoading, hasPermission } from '$lib/auth/stores';
	import { authActions } from '$lib/auth/api';

	export let requiredPermission: { resource: string; action: string } | null = null;

	onMount(() => {
		// Initialize authentication state
		authActions.initializeAuth();
	});

	$: {
		if (!$isLoading) {
			if (!$isAuthenticated) {
				const redirectUrl = `/login?redirect=${encodeURIComponent($page.url.pathname)}`;
				goto(redirectUrl);
			} else if (requiredPermission && !$hasPermission(requiredPermission.resource, requiredPermission.action)) {
				goto('/unauthorized');
			}
		}
	}
</script>

{#if $isLoading}
	<div class="d-flex flex-column align-items-center justify-content-center min-vh-100 bg-light">
		<div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
			<span class="visually-hidden">Loading...</span>
		</div>
		<p class="mt-3 text-muted">Loading SantaServer...</p>
	</div>
{:else if $isAuthenticated && (!requiredPermission || $hasPermission(requiredPermission.resource, requiredPermission.action))}
	<slot />
{/if}
