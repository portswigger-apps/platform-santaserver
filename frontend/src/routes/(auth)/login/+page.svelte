<!-- src/routes/(auth)/login/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { isAuthenticated } from '$lib/auth/stores';
  import LoginForm from '$lib/components/auth/LoginForm.svelte';
  
  onMount(() => {
    // If already authenticated, redirect to dashboard or redirect URL
    if ($isAuthenticated) {
      const redirectUrl = $page.url.searchParams.get('redirect') || '/dashboard';
      goto(redirectUrl);
    }
  });

  // Watch for authentication changes
  $: if ($isAuthenticated) {
    const redirectUrl = $page.url.searchParams.get('redirect') || '/dashboard';
    goto(redirectUrl);
  }
</script>

<svelte:head>
  <title>Sign in - SantaServer</title>
  <meta name="description" content="Sign in to SantaServer - Enterprise Santa Management Platform" />
</svelte:head>

<div class="login-page">
  <div class="login-container">
    <LoginForm />
  </div>
</div>

<style>
  .login-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
  }

  .login-container {
    width: 100%;
    max-width: 400px;
  }

  @media (max-width: 640px) {
    .login-page {
      padding: 0.5rem;
    }
  }
</style>