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

<div class="login-page bg-gradient-dark min-vh-100 d-flex align-items-center justify-content-center">
	<div class="container">
		<div class="row justify-content-center">
			<div class="col-12 col-sm-8 col-md-6 col-lg-4">
				<LoginForm />
			</div>
		</div>
	</div>
</div>
