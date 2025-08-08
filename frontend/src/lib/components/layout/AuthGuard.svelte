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
  <div class="loading">
    <div class="spinner"></div>
    <p>Loading...</p>
  </div>
{:else if $isAuthenticated && (!requiredPermission || $hasPermission(requiredPermission.resource, requiredPermission.action))}
  <slot />
{/if}

<style>
  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    color: #6b7280;
  }

  .spinner {
    width: 2rem;
    height: 2rem;
    border: 2px solid #e5e7eb;
    border-top: 2px solid #2563eb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>